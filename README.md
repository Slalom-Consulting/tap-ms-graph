# tap-ms-graph

`tap-ms-graph` is a Singer tap for MSGraph.

Built with the [Meltano Tap SDK](https://sdk.meltano.com) for Singer Taps and the [Microsoft Graph API reference](https://learn.microsoft.com/en-us/graph/api/overview?view=graph-rest-1.0&preserve-view=true).

<!--

Developer TODO: Update the below as needed to correctly describe the install procedure. For instance, if you do not have a PyPi repo, or if you want users to directly install from your git repo, you can modify this step as appropriate.

## Installation

Install from PyPi:

```bash
pipx install tap-ms-graph
```
-->

Install from GitHub:

```bash
pipx install git+https://github.com/Slalom-Consulting/tap-ms-graph.git@main
```

## Capabilities

* `catalog`
* `state`
* `discover`
* `about`
* `stream-maps`
* `schema-flattening`

## Configuration

### Accepted Config Options

<!--
Developer TODO: Provide a list of config options accepted by the tap.

This section can be created by copy-pasting the CLI output from:

```
tap-ms-graph --about --format=markdown
```
-->

| Setting             | Required | Default | Description |
|:--------------------|:--------:|:-------:|:------------|
| tenant              | True     | None    | The directory tenant that you want to request permission from. The value can be in GUID or a friendly name format. |
| client_id           | True     | None    | The application ID that the Azure app registration portal assigned when you registered your app. |
| client_secret       | True     | None    | The client secret that you generated for your app in the app registration portal. |
| stream_config       | False    | None    | Custom configuration for streams. |
| api_version         | False    | v1.0    | The version of the Microsoft Graph API to use |
| auth_url            | False    | None    | Override the Azure AD authentication base URL. Required if using a national cloud. |
| api_url             | False    | None    | Override the Graph API service base URL. Required if using a national cloud. |

A full list of supported settings and capabilities for this
tap is available by running:

```bash
tap-ms-graph --about
```

### Settings for Specific Streams

Settings can be added on a per-stream basis and can be set using the stream_config setting. The stream_config setting takes a dictionary with the stream name as the key and supports the following configuration options:

| Setting             | Required | Default | Description |
|:--------------------|:--------:|:-------:|:------------|
| parameters          | False    | None    | URL query string to send to the stream endpoint |

#### Stream Parameters

Many streams support [advanced query capabilities](https://learn.microsoft.com/en-us/graph/aad-advanced-queries?tabs=http) (eg. `$count`, `$select`, `$filter`, `$search`, `$orderby`, ...) and can be added to the tap configuration stream parameters.

Example:

```json
# config.json

{
    "stream_config": {
        "users": {
            "parameters": "?$select=id"
        }
    }
}
```

### Configure using environment variables

This Singer tap will automatically import any environment variables within the working directory's
`.env` if the `--config=ENV` is provided, such that config values will be considered if a matching
environment variable is set either in the terminal context or in the `.env` file.

<!--
### Source Authentication and Authorization

Developer TODO: If your tap requires special access on the source system, or any special authentication requirements, provide those here.
-->

## Usage

You can easily run `tap-ms-graph` by itself or in a pipeline using [Meltano](https://meltano.com/).

### Executing the Tap Directly

```bash
tap-ms-graph --version
tap-ms-graph --help
tap-ms-graph --config CONFIG --discover > ./catalog.json
```

## Developer Resources

Follow these instructions to contribute to this project.

### Initialize your Development Environment

```bash
pipx install poetry
poetry install
```

### Create and Run Tests

Create tests within the `tap_ms_graph/tests` subfolder and
  then run:

```bash
poetry run pytest
```

You can also test the `tap-ms-graph` CLI interface directly using `poetry run`:

```bash
poetry run tap-ms-graph --help
```

### Testing with [Meltano](https://www.meltano.com)

_**Note:** This tap will work in any Singer environment and does not require Meltano.
Examples here are for convenience and to streamline end-to-end orchestration scenarios._

<!--
Developer TODO:
Your project comes with a custom `meltano.yml` project file already created. Open the `meltano.yml` and follow any "TODO" items listed in
the file.
-->

Next, install Meltano (if you haven't already) and any needed plugins:

```bash
# Install meltano
pipx install meltano
# Initialize meltano within this directory
cd tap-ms-graph
meltano install
```

Now you can test and orchestrate using Meltano:

```bash
# Test invocation:
meltano invoke tap-ms-graph --version
# OR run a test `elt` pipeline:
meltano elt tap-ms-graph target-jsonl
```

### SDK Dev Guide

See the [dev guide](https://sdk.meltano.com/en/latest/dev_guide.html) for more instructions on how to use the SDK to
develop your own taps and targets.