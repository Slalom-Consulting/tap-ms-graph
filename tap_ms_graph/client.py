"""REST client handling, including MSGraphStream base class."""

from typing import Any, Dict, Optional, Callable, Generator
from enum import Enum
from singer_sdk.streams import RESTStream
from tap_ms_graph.auth import MSGraphAuthenticator
from singer_sdk.pagination import JSONPathPaginator
from memoization import cached
from pathlib import Path
from urllib.parse import urljoin, urlsplit, parse_qs


SCHEMAS_DIR = Path(__file__).parent / Path('./schemas')
API_URL = 'https://graph.microsoft.com'


class ApiVersion(str, Enum):
    beta = 'beta'
    v1 = 'v1.0'


class MSGraphStream(RESTStream):
    """MSGraph stream class."""
    @property
    def url_base(self) -> str:
        """Return the API URL root, configurable via tap settings."""
        base = self.config.get('api_url', API_URL)
        version = ApiVersion[self.config.get('api_version')].value
        return urljoin(base, version)

    records_jsonpath = '$.value[*]'
    next_page_token_jsonpath = "$.@odata.nextLink"

    @property
    @cached
    def authenticator(self) -> MSGraphAuthenticator:
        """Return a new authenticator object."""
        return MSGraphAuthenticator(self)

    def get_new_paginator(self) -> JSONPathPaginator:
        return JSONPathPaginator(self.next_page_token_jsonpath)

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed."""
        headers = {}
        
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")

        #TODO Add special header if specific parameter exists in query
        
        return headers

    def backoff_wait_generator(self) -> Callable[..., Generator[int, Any, None]]:
        def _backoff_from_headers(retriable_api_error) -> int:
            response_headers = retriable_api_error.response.headers
            return int(response_headers.get('Retry-After', 0))

        return self.backoff_runtime(value=_backoff_from_headers)

    def get_url_params(self, context: Optional[dict], next_page_token: Optional[str]) -> Dict[str, Any]:
        if next_page_token:
            return parse_qs(urlsplit(next_page_token).query)

        return super().get_url_params(context, None)
