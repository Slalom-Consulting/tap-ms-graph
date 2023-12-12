import pytest
import mock
import responses
from responses import POST, GET

from tap_ms_graph.tap import TapMSGraph

SERVICE_PRINIPLE_CONFIG = {
        "tenant" : "123",
        "client_id" : "123",
        "client_secret" : "123",
        }

DEFAULT_CRED_CONFIG = {
        "tenant" : "123"
        }

MANAGED_IDNETITY_CONFIG = {
        "tenant": "123",
        "managed_identity": "1223345"
       }

WORKLOAD_IDENTITY_CONFIG = {
        "tenant": "123",
        "workload_identity": "123"
        }


@pytest.fixture
def mock_az_default_identity():
    with mock.patch(
        "azure.identity.DefaultAzureCredential.get_token",
    ) as mock_get_token:
        mock_get_token.return_value = mock.Mock(token="Deafult_identity_token")
        yield mock_get_token


@pytest.fixture
def mock_az_managed_identity():
    with mock.patch(
        "azure.identity.ManagedIdentityCredential.get_token",
    ) as mock_get_token:
        mock_get_token.return_value = mock.Mock(token="Managed_identity_token")
        yield mock_get_token


@pytest.fixture
def mock_az_service_principle():
    with mock.patch(
            "singer_sdk.authenticators.OAuthAuthenticator.token_response",
    ) as mock_get_token:
        mock_get_token.return_value = mock.Mock(token="Service_principle_token")
        yield mock_get_token


def test_managed_identity_call(mock_az_managed_identity):
    tap1 = TapMSGraph(MANAGED_IDNETITY_CONFIG)
    stream = tap1.discover_streams()[0]
    assert stream.authenticator.auth_headers == {'Authorization': 'Bearer Managed_identity_token'}


def test_default_credentials_call(mock_az_default_identity, mock_az_managed_identity):
    tap1 = TapMSGraph(DEFAULT_CRED_CONFIG)
    stream = tap1.discover_streams()[0]
    assert stream.authenticator.auth_headers == {'Authorization': 'Bearer Deafult_identity_token'}

@responses.activate
def test_service_principle_call(mock_az_default_identity, mock_az_managed_identity):
    tap1 = TapMSGraph(SERVICE_PRINIPLE_CONFIG)
    responses.add(POST,
                  "https://login.microsoftonline.com/123/oauth2/v2.0/token",
                  json={'access_token': 'Service_principle_token'},
                  status=200
                  )
    stream = tap1.discover_streams()[0]
    assert stream.authenticator.auth_headers == {'Authorization': 'Bearer Service_principle_token'}
