"""MSGraph tap class."""

from typing import List

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_ms_graph.streams import (
    GroupMembersStream,
    GroupsStream,
    SubscribedSkusStream,
    UsersStream,
)

STREAM_TYPES = [
    GroupsStream,
    GroupMembersStream,
    SubscribedSkusStream,
    UsersStream,
]


class TapMSGraph(Tap):
    """MSGraph tap class."""

    name = "tap-ms-graph"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "tenant",
            th.StringType,
            required=True,
            description="The directory tenant to request permission from. \
                The value can be in GUID or a friendly name format.",
        ),
        th.Property(
            "client_id",
            th.StringType,
            required=True,
            description="The application ID that the Azure app registration \
                portal assigned to the registered app.",
        ),
        th.Property(
            "client_secret",
            th.StringType,
            required=True,
            secret=True,
            description="The client secret generated for the app \
                in the app registration portal.",
        ),
        th.Property(
            "stream_config",
            th.ObjectType(
                additional_properties=th.ObjectType(
                    th.Property(
                        "parameters",
                        th.StringType,
                        description="URL formatted parameters string to \
                            be used for stream.",
                    ),
                )
            ),
            description="Custom configuration for streams.",
        ),
        th.Property(
            "include_odata_type",
            th.BooleanType,
            default=False,
            allowed_values=[True, False],
            description="Include '@odata_type' field when returned from API.",
        ),
        th.Property(
            "api_version",
            th.StringType,
            default="v1.0",
            allowed_values=["v1.0", "beta"],
            description="The version of the Microsoft Graph API to use.",
        ),
        th.Property(
            "auth_url",
            th.StringType,
            description="Override the Azure AD authentication base URL. \
                Required if using a national cloud.",
        ),
        th.Property(
            "api_url",
            th.StringType,
            description="Override the Graph API service base URL. \
                Required if using a national cloud.",
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        """Return a list of discovered streams."""
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == "__main__":
    TapMSGraph.cli()
