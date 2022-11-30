"""Stream type classes for tap-ms-graph."""

from pathlib import Path
from typing import Any, Dict, Optional, Union, List, Iterable
from tap_ms_graph.client import MSGraphStream


SCHEMAS_DIR = Path(__file__).parent / Path('./schemas')

class UsersStream(MSGraphStream):
    """Define custom stream."""
    name = 'users'
    path = '/users'
    primary_keys = ['id']
    replication_key = None

    @property
    def schema_filepath(self) -> str:
        return SCHEMAS_DIR / self.version / 'users.json'
    
    @property
    def query(self):
        return self.config.get('users_stream_query')

