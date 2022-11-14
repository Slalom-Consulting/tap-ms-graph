"""Stream type classes for tap-ms-graph."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable
from tap_ms_graph.client import MSGraphStream


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")

class UsersStream(MSGraphStream):
    """Define custom stream."""
    name = "users"
    path = "/users"
    primary_keys = ["id"]
    replication_key = None
    schema_filepath = SCHEMAS_DIR / "users.json"


class UserLicenseDetailsStream:
    name = "users"
    path = "/users"
    primary_keys = ["id"]

    @property
    def http_headers(self) -> dict:
        headers = super().http_headers or {}
        headers['ConsistencyLevel'] = 'eventual'

'''
https://graph.microsoft.com/v1.0/users?$count=true&$filter=assignedLicenses/$count+ne+0+and+accountEnabled+eq+true
'''