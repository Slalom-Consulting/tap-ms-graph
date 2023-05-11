"""Stream type classes for tap-ms-graph."""
from typing import Optional

from tap_ms_graph.client import MSGraphStream


class GroupsStream(MSGraphStream):
    name = "groups"
    path = "/groups"
    primary_keys = ["id"]
    replication_key = None
    odata_context = "groups"

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        """Return a context dictionary for child streams."""
        return {
            "id": record["id"],
        }


class GroupMembersStream(MSGraphStream):
    parent_stream_type = GroupsStream
    name = "group_members"
    path = "/groups/{id}/members"
    primary_keys = ["id"]
    replication_key = None
    odata_context = "groups"


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
