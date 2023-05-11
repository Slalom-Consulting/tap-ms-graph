"""Tests standard tap features using the built-in SDK tests library."""


from singer_sdk.testing import get_standard_tap_tests

from tap_ms_graph.tap import TapMSGraph

SAMPLE_CONFIG = {
    "tenant": "00000000-0000-0000-0000-000000000000",
    "client_id": "00000000-0000-0000-0000-000000000000",
    "client_secret": "test",
}


# Run standard built-in tap tests from the SDK:
def test_standard_tap_tests():
    """Run standard tap tests from the SDK."""
    tests = get_standard_tap_tests(TapMSGraph, config=SAMPLE_CONFIG)
    for test in tests:
        if test.__name__ in ("_test_stream_connections"):
            continue

        test()


# TODO: Create additional tests as appropriate for your tap.
