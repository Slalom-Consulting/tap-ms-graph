"""Stream type classes for tap-ms-graph."""

from tap_ms_graph.client import MSGraphStream


# V1.0
class SubscribedSkusStream(MSGraphStream):
    name = "subscribedSkus"
    path = "/subscribedSkus"
    primary_keys = ["id"]
    replication_key = None
    odata_context = "subscribedSkus"
    # schema_filename = "subscribedSkus.json"


class UsersStream(MSGraphStream):
    name = "users"
    path = "/users"
    primary_keys = ["id"]
    replication_key = None
    odata_context = "users"
    # schema_filename = "users.json"
