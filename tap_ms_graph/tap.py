"""MSGraph tap class."""

from typing import List

from singer_sdk import Stream, Tap
from singer_sdk import typing as th

from tap_ms_graph.streams import UsersStream

STREAM_TYPES = [
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
            th.ArrayType(
                th.PropertiesList(
                    th.Property(
                        "stream",
                        th.StringType,
                        required=True,
                        description="Name of stream to apply a custom configuration.",
                    ),
                    th.Property(
                        "parameters",
                        th.StringType,
                        description="URL formatted parameters string to \
                            be used for stream.",
                    ),
                    # th.Property(
                    #    "primary_keys",
                    #    th.ArrayType(th.StringType),
                    #    description="Override the default list of primary keys.",
                    # ),
                    # th.Property(
                    #    "replication_key",
                    #    th.StringType,
                    #    description="Override the default replication key.",
                    # ),
                    # th.Property(
                    #    "schema_discovery",
                    #    th.BooleanType,
                    #    description="Override the default schema \
                    # and use discovery mode.",
                    # ),
                    # th.Property(
                    #    "schema",
                    #    th.StringType,
                    #    description="Override the default schema \
                    # with a custom JSONSchema string.",
                    # ),
                )
            ),
            description="Custom configuration for streams.",
        ),
        th.Property(
            "api_version",
            th.StringType,
            default="v1.0",
            # allowed_values=['v1.0', 'beta'],
            allowed_values=["v1.0"],
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
