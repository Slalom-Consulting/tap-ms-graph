"""REST client handling, including MSGraphStream base class."""

from typing import Any, Callable, Generator, Iterable, Union, Optional
from enum import Enum
from singer_sdk.streams import RESTStream
from tap_ms_graph.auth import MSGraphAuthenticator
from singer_sdk.pagination import JSONPathPaginator
from memoization import cached
from pathlib import Path
from urllib.parse import urljoin
import uuid
import requests
import json


SCHEMAS_DIR = Path(__file__).parent / Path('./schemas')
API_URL = 'https://graph.microsoft.com'


class ApiVersion(str, Enum):
    beta = 'beta'
    v1 = 'v1.0'


class MSGraphStream(RESTStream):
    """MSGraph stream class."""
    @property
    def url_base(self) -> str:
        base = self.config.get('api_url', API_URL)
        version = ApiVersion[self.config.get('api_version')].value
        return urljoin(base, version)

    records_jsonpath = '$.value[*]'
    record_child_context = 'id'
    next_page_token_jsonpath = '$.@odata.nextLink'

    @property
    @cached
    def authenticator(self) -> MSGraphAuthenticator:
        return MSGraphAuthenticator(self)

    def get_new_paginator(self) -> JSONPathPaginator:
        return JSONPathPaginator(self.next_page_token_jsonpath)

    @property
    def http_headers(self) -> dict:
        headers = {}

        if self.get_url_params.get('$count') in ['true', True]:
            headers['ConsistencyLevel'] = 'eventual'

        if self.config.get('log_requests'):
            id = str(uuid.uuid4())
            headers['client-request-id'] = id
            log_text = json.dumps({'client-request-id': id})
            self.logger.info(f'Microsoft Graph request log: {log_text}')
        
        return headers

    def backoff_wait_generator(self) -> Callable[..., Generator[int, Any, None]]:
        def _backoff_from_headers(retriable_api_error) -> int:
            response_headers = retriable_api_error.response.headers
            return int(response_headers.get('Retry-After', 0))

        return self.backoff_runtime(value=_backoff_from_headers)

    def prepare_request(self, context: Union[dict, None], next_page_token: Union[Any, None]) -> requests.PreparedRequest:
        prepared_request = super().prepare_request(context, None)
        
        if next_page_token:
            prepared_request.url = next_page_token

        return prepared_request

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        if self.config.get('log_requests'):
            log_keys = ['request-id', 'Date', 'x-ms-ags-diagnostic']
            log_headers = {k:v for k,v in response.headers if k in log_keys}
            log_text = json.dumps(log_headers)
            self.logger.info(f'Microsoft Graph response log: {log_text}')

        return super().parse_response(response)
    
    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        if self.record_child_context:
            return record.get(self.record_child_context)
