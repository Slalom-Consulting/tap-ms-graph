"""REST client handling, including MSGraphStream base class."""

from __future__ import annotations

import json
import uuid

# from pathlib import Path
from typing import Any, Dict, Generator, Iterable, Optional, Union
from urllib.parse import parse_qsl, urljoin

import requests
from memoization import cached
from singer_sdk.streams import RESTStream

from tap_ms_graph.auth import MSGraphAuthenticator
from tap_ms_graph.pagination import MSGraphPaginator
from tap_ms_graph.schema import get_schema, get_type_schema

API_URL = "https://graph.microsoft.com"


class MSGraphStream(RESTStream):
    """MSGraph stream class."""

    records_jsonpath = "$.value[*]"

    # configure per stream
    primary_keys = []
    odata_context = ""
    odata_type = ""
    child_context = {}

    @property
    def api_version(self) -> str:
        """Get API version."""
        return str(self.config.get("api_version", ""))

    @property
    def schema(self):
        link = "{host}/{version}/$metadata#{endpoint}"

        odata_context = link.format(
            host=API_URL, version=self.api_version, endpoint=self.odata_context
        )

        schema = get_schema(odata_context)

        if self.odata_type:
            type_schema = get_type_schema(odata_context, self.odata_type)
            type_properties = type_schema.get("properties", {})

            schema["properties"] = {**schema["properties"], **type_properties}

        return schema

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
        if str(params.get("$count", "")).lower() == "true":
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
            conf for conf in stream_configs if conf.get("stream", "") == self.name
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
        filter_params = params.get("$filter", "")
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

    def post_process(self, row: dict, context: dict | None = None) -> dict | None:
        # converts complex types to string

        new_row = row.copy()
        for k, v in row.items():
            if isinstance(v, dict) or isinstance(v, list):
                new_row[k] = json.dumps(v)

        return new_row

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        return {v: record[k] for k, v in self.child_context.items()}
