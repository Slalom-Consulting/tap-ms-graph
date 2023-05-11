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
    primary_keys = ["group_id", "id"]
    replication_key = None
    odata_context = "groups"

    @property
    def schema(self):
        schema = super().schema
        added_schema = {"group_id": {"type": "string"}}

        schema["properties"] = {**added_schema, **schema["properties"]}

        return schema

    def post_process(self, row: dict, context: Optional[dict] = None) -> dict:
        return {**{"group_id": context.get("id")}, **row}


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
