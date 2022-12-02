"""MSGraph tap class."""

from typing import List
from singer_sdk import Tap, Stream
from singer_sdk import typing as th


from tap_ms_graph.streams import (
    UsersStream,
)

STREAM_TYPES = [
    UsersStream,
]


class TapMSGraph(Tap):
    '''MSGraph tap class.'''
    name = 'tap-ms-graph'

    config_jsonschema = th.PropertiesList(
        th.Property(
            'tenant',
            th.StringType,
            required=True,
            description='The directory tenant that you want to request permission from. The value can be in GUID or a friendly name format.'
        ),
        th.Property(
            'client_id',
            th.StringType,
            required=True,
            description='The application ID that the Azure app registration portal assigned when you registered your app.'
        ),
        th.Property(
            'client_secret',
            th.StringType,
            required=True,
            secret=True,
            description='The client secret that you generated for your app in the app registration portal.'
        ),
        th.Property(
            'stream_config',
            th.ArrayType(
                th.PropertiesList(
                    th.Property(
                        'stream',
                        th.StringType,
                        description='Name of stream to apply config.'
                    ),
                    th.Property(
                        'params',
                        th.ArrayType(
                            th.PropertiesList(
                                th.Property(
                                    'param',
                                    th.StringType,
                                    description='Name of query parameter.'
                                ),
                                th.Property(
                                    'value',
                                    th.StringType,
                                    description='Value of query parameter.'
                                )
                            )
                        )
                    )
                )
            ),
            description='Custom configuration for streams.'
        ),
#        th.Property(
#            'start_date',
#            th.DateTimeType,
#            description='The earliest record date to sync'
#        ),
        th.Property(
            'api_version',
            th.StringType,
            default='v1.0',
            #allowed_values=['v1', 'beta'],
            description='The version of the Microsoft Graph API to use'
        ),
        th.Property(
            'auth_url',
            th.StringType,
            description='Override the Azure AD authentication base URL. Required if using a national cloud.'
        ),
        th.Property(
            'api_url',
            th.StringType,
            description='Override the Graph API service base URL. Required if using a national cloud.'
        ),
    ).to_dict()

    def discover_streams(self) -> List[Stream]:
        '''Return a list of discovered streams.'''
        return [stream_class(tap=self) for stream_class in STREAM_TYPES]


if __name__ == '__main__':
    TapMSGraph.cli()
