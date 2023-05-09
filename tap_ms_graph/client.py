"""REST client handling, including MSGraphStream base class."""

import json
import uuid
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, Optional, Union
from urllib.parse import parse_qsl, urljoin

import requests
from memoization import cached
from singer_sdk.streams import RESTStream

from tap_ms_graph.auth import MSGraphAuthenticator
from tap_ms_graph.pagination import MSGraphPaginator

API_URL = "https://graph.microsoft.com"
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class MSGraphStream(RESTStream):
    """MSGraph stream class."""

    records_jsonpath = "$.value[*]"
    record_child_context = "id"
    schema_filename: str = ""  # configure per stream
    primary_keys = []  # configure per stream

    @property
    def api_version(self) -> str:
        """Get API version"""
        return str(self.config.get("api_version"))

    @property
    def schema_filepath(self) -> str:
        api_path = SCHEMAS_DIR.joinpath(self.api_version)
        return str(api_path.joinpath(self.schema_filename))

    @property
    def url_base(self) -> str:
        base = self.config.get("api_url", API_URL)
        return urljoin(base, self.api_version)

    @property
    @cached  # type: ignore[override]
    def authenticator(self) -> MSGraphAuthenticator:
        return MSGraphAuthenticator(self)

    @property
    def http_headers(self) -> dict:
        headers = {}

        # Set ConsistencyLevel for count operations
        params = self.get_url_params(None, None) or {}
        if str(params.get("$count")).lower() == "true":
            headers["ConsistencyLevel"] = "eventual"

        # Configure request logging
        id = str(uuid.uuid4())
        headers["client-request-id"] = id
        log_text = json.dumps({"client-request-id": id})
        self.logger.info(f"INFO request: {log_text}")

        return headers

    def backoff_wait_generator(self) -> Generator[int, Any, None]:
        def _backoff_from_headers(retriable_api_error) -> int:
            response_headers = retriable_api_error.response.headers
            return int(response_headers.get("Retry-After", 0))

        return self.backoff_runtime(value=_backoff_from_headers)

    def get_new_paginator(self) -> MSGraphPaginator:
        return MSGraphPaginator()

    def _get_stream_config(self) -> dict:
        """Get parameters set in config."""
        config: dict = {}

        stream_configs = self.config.get("stream_config", [])
        if not stream_configs:
            return config

        config_list = [
            conf for conf in stream_configs if conf.get("stream") == self.name
        ] or [None]
        config_dict = config_list[-1] or {}
        stream_config = {k: v for k, v in config_dict.items() if k != "stream"}
        return stream_config

    def _get_stream_params(self) -> dict:
        stream_params = self._get_stream_config().get("parameters", "")
        return {qry[0]: qry[1] for qry in parse_qsl(stream_params.lstrip("?"))}

    def get_url_params(
        self, context: Optional[dict], next_page_token: Optional[Any]
    ) -> Dict[str, Any]:
        params = self._get_stream_params()

        # Ensure that $count is True when used in $filter parameter
        filter_params = params.get("$filter", str)
        if filter_params:
            if "$count" in filter_params:
                params["$count"] = True

        # Ensure that primary keys are included in $select parameter
        select_param = params.get("$select", "")
        if select_param:
            select_params = select_param.split(",")

            missing_primary_keys = [
                k for k in self.primary_keys if k not in select_params
            ]

            if missing_primary_keys:
                select_params.extend(missing_primary_keys)

            params["$select"] = ",".join(select_params)

        return params

    def prepare_request(
        self, context: Union[dict, None], next_page_token: Union[Any, None]
    ) -> requests.PreparedRequest:
        # Pass next page url through to request as opaque string
        prepared_request = super().prepare_request(context, None)

        if next_page_token:
            prepared_request.url = next_page_token

        return prepared_request

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        # Response logging
        headers = response.headers

        logging_headers = {
            "client-request-id": headers.get("client-request-id"),
            "request-id": headers.get("request-id"),
            "Date": headers.get("Date"),
            "x-ms-ags-diagnostic": json.loads(str(headers.get("x-ms-ags-diagnostic"))),
        }

        log_text = json.dumps(logging_headers)
        self.logger.info(f"INFO response: {log_text}")

        return super().parse_response(response)

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        child_context = {}

        if self.record_child_context:
            child_context = record[self.record_child_context]

        return child_context
