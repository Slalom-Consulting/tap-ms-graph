# Adding a new stream

Add the following to [streams.py](streams.py):

## Regular stream

```python
# streams.py

class NameStream(MSGraphStream):
    name = "streamName"
    path = "/streamEndpoint"
    primary_keys = ["id"]
    odata_context = "streamOdataContext"
```

## Child Stream

Add the following to the parent stream, and modify if needed with the return dict with the values to pass to the child stream:

```python
# streams.py
# class ParentStream(MSGraphStream):

    child_context = {"field": "parent_field"}
```

Then add the new child stream:

```python
# streams.py

class NameStream(MSGraphChildStream):
    parent_stream_type = ParentStream
    name = "streamName"
    path = "parentEndpoint/{parent_field}/streamEndpoint"
    primary_keys = ["id"]
    odata_context = "streamOdataContext"
    odata_type = "streamOdataType"  # optional

    parent_context_schema = {
        "parent_field": {"type": "string"},
    }
```