"""Stream type classes for tap-ms-graph."""
from __future__ import annotations

from tap_ms_graph.client import MSGraphChildStream, MSGraphStream


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


class TeamsStream(MSGraphChildStream):
    parent_stream_type = GroupsStream
    name = "teams"
    path = "/teams/{group_id}"
    primary_keys = ["id"]
    odata_context = "teams/$entity"
    child_context = {"id": "team_id"}
    #$filter=resourceProvisioningOptions/any(i:i eq 'Team')


class TeamChannelsStream(MSGraphChildStream):
    parent_stream_type = TeamsStream
    name = "teamChannels"
    path = "/teams/{team_id}/channels"
    primary_keys = ["team_id", "id"]
    odata_context = "#teams/channels"
    child_context = {"id": "channel_id"}

    parent_context_schema = {
        "team_id": {"type": "string"},
    }

class TeamChannelMembersStream(MSGraphChildStream):
    parent_stream_type = TeamChannelsStream
    name = "groups"
    path = "/teams/{team_id}/channel/{channel_id}/members"
    primary_keys = ["team_id", "channel_id", "id"]
    odata_context = "teams/$entity"
    #$filter=resourceProvisioningOptions/any(i:i eq 'Team')

    parent_context_schema = {
        "team_id": {"type": "string"},
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
