"""Stream type classes for tap-ms-graph."""
from __future__ import annotations

from typing import Optional

from tap_ms_graph.client import MSGraphStream


class GroupsStream(MSGraphStream):
    name = "groups"
    path = "/groups"
    primary_keys = ["id"]
    replication_key = None
    odata_context = "groups"

    def get_child_context(self, record: dict, context: Optional[dict]) -> dict:
        return {"id": record["id"]}


class GroupMembersStream(MSGraphStream):
    parent_stream_type = GroupsStream
    name = "group_members"
    path = "/groups/{id}/members"
    primary_keys = ["group_id", "id"]
    replication_key = None
    odata_context = "directoryObjects"
    odata_type = "microsoft.graph.user"

    @property
    def schema(self):
        schema = super().schema
        parent_schema = {
            "@odata.type": {"type": ["string", "null"]},
            "group_id": {"type": "string"},
        }
        schema["properties"] = {**parent_schema, **schema["properties"]}

        return schema

    def post_process(self, row: dict, context: dict | None = None) -> dict:
        simplified_row = super().post_process(row, context) or {}

        if context:
            parent_fields = {"group_id": context.get("id", "")}
            return {**parent_fields, **simplified_row}

        return simplified_row


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
