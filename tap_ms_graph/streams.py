"""Stream type classes for tap-ms-graph."""
from __future__ import annotations

from tap_ms_graph.client import MSGraphStream


class MSGraphChildStream(MSGraphStream):
    parent_context_schema: dict = {}

    @property
    def schema(self):
        schema = super().schema
        odata_type = {"@odata.type": {"type": ["string", "null"]}}

        schema["properties"] = {
            **self.parent_context_schema,
            **odata_type,
            **schema["properties"],
        }

        return schema

    def post_process(self, row: dict, context: dict | None = None) -> dict:
        processed_row = super().post_process(row, context) or {}

        if context:
            context_fields = {k: context.get(k, "") for k in context.keys()}
            return {**context_fields, **processed_row}

        return processed_row


class GroupsStream(MSGraphStream):
    name = "groups"
    path = "/groups"
    primary_keys = ["id"]
    odata_context = "groups"

    child_context = {"id": "group_id"}


class GroupMembersStream(MSGraphChildStream):
    parent_stream_type = GroupsStream
    name = "groupMembers"
    path = "/groups/{group_id}/members"
    primary_keys = ["group_id", "id"]
    odata_context = "directoryObjects"
    odata_type = "microsoft.graph.user"

    # TODO: find a way to make this automatic
    parent_context_schema = {
        "group_id": {"type": "string"},
    }


class SubscribedSkusStream(MSGraphStream):
    name = "subscribedSkus"
    path = "/subscribedSkus"
    primary_keys = ["id"]
    odata_context = "subscribedSkus"


class UsersStream(MSGraphStream):
    name = "users"
    path = "/users"
    primary_keys = ["id"]
    odata_context = "users"
