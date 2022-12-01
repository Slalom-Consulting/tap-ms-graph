"""Stream type classes for tap-ms-graph."""

from tap_ms_graph.client import MSGraphStream


class UsersStream(MSGraphStream):
    """Define custom stream."""
    name = 'users'
    path = '/users'
    primary_keys = ['id']
    replication_key = None
    schema_filename = 'users.json'
