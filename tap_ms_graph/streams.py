"""Stream type classes for tap-ms-graph."""

from tap_ms_graph.client import MSGraphStream


class SubscribedSkusStream(MSGraphStream):
    name = "subscribedSkus"
    path = "/subscribedSkus"
    primary_keys = ["id"]
    replication_key = None
    odata_context = "subscribedSkus"


class UsersStream(MSGraphStream):
    name = "users"
    path = "/users"
    primary_keys = ["id"]
    replication_key = None
    odata_context = "users"


class GroupsStream(MSGraphStream):
    name = "groups"
    path = "/groups"
    primary_keys = ["id"]
    replication_key = None
    odata_context = "groups"


class GroupMembersStream(MSGraphStream):
    name = "groups"
    path = "/groups/{id}/members"
    primary_keys = ["id"]
    replication_key = None
    odata_context = "groups"
