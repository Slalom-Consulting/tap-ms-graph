"""REST client handling, including MSGraphStream base class."""

from typing import Any, Callable, Generator, Iterable, Union, Optional, Dict
from singer_sdk.streams import RESTStream
from tap_ms_graph.auth import MSGraphAuthenticator
from tap_ms_graph.pagination import MSGraphPaginator
from memoization import cached
from urllib.parse import urljoin
from pathlib import Path
import uuid
import requests
import json


API_URL = 'https://graph.microsoft.com'
SCHEMAS_DIR = Path(__file__).parent / Path('./schemas')


class MSGraphStream(RESTStream):
    """MSGraph stream class."""

    records_jsonpath = '$.value[*]'
    record_child_context = 'id'
    schema_filename:str = None   # configure per stream

    @property
    def api_version(self) -> str:
        return self.config.get('api_version')

    @property
    def schema_filepath(self) -> str:
        #return f'{SCHEMAS_DIR}/{self.api_version}/{self.schema_filename}'
        return f'{SCHEMAS_DIR}/v1.0/{self.schema_filename}'

    @property
    def url_base(self) -> str:
        base = self.config.get('api_url', API_URL)
        return urljoin(base, self.api_version)

    @property
    @cached
    def authenticator(self) -> MSGraphAuthenticator:
        return MSGraphAuthenticator(self)

    @property
    def http_headers(self) -> dict:
        headers = {}
        params = self.get_url_params(None, None) or {}

        if str(params.get('$count')).lower() == 'true':
            headers['ConsistencyLevel'] = 'eventual'

        id = str(uuid.uuid4())
        headers['client-request-id'] = id
        log_text = json.dumps({'client-request-id': id})
        self.logger.info(f'INFO request: {log_text}')
        
        return headers

    def backoff_wait_generator(self) -> Callable[..., Generator[int, Any, None]]:
        def _backoff_from_headers(retriable_api_error) -> int:
            response_headers = retriable_api_error.response.headers
            return int(response_headers.get('Retry-After', 0))

        return self.backoff_runtime(value=_backoff_from_headers)

    def get_new_paginator(self) -> MSGraphPaginator:
        return MSGraphPaginator()

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        stream_config = self.config.get('stream_config')
        
        if stream_config:
            params = [c.get('params') for c in stream_config if c.get('stream') == self.name]
            
            if params:
                return {p.get('param'):p.get('value') for p in params[-1]}

    def prepare_request(
        self, context: Union[dict, None], next_page_token: Union[Any, None]
    ) -> requests.PreparedRequest:
        prepared_request = super().prepare_request(context, None)

        if next_page_token:
            prepared_request.url = next_page_token

        return prepared_request

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        headers = response.headers

        logging_headers = {
            'client-request-id': headers.get('client-request-id'),
            'request-id': headers.get('request-id'),
            'Date': headers.get('Date'),
            'x-ms-ags-diagnostic': json.loads(headers.get('x-ms-ags-diagnostic'))
        }
        
        log_text = json.dumps(logging_headers)
        self.logger.info(f'INFO response: {log_text}')

        return super().parse_response(response)

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        if self.record_child_context:
            return record.get(self.record_child_context)
