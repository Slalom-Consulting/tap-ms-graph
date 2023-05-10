import re
from urllib.parse import urlsplit
from pathlib import Path

import jsonref
from memoization import cached


SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")
VERSION = "{version}"
METADATA_FILE = f"{SCHEMAS_DIR}/{VERSION}/metadata.json"


@cached
def load_metadata(version: str) -> dict:
    file = METADATA_FILE.format(version=version)

    with open(file, "r") as fp:
        metadata = jsonref.load(fp)

    return metadata


def get_ref(context: str) -> dict:
    link = urlsplit(context)
    version = link.path.split("/")[1]
    metadata = load_metadata(version)

    for ref in metadata.get("anyOf", []):
        properties = ref.get("properties", {})
        odata_context = properties.get("@odata.context", {})
        pattern = odata_context.get("pattern", "")
        context_str = f"$metadata#{link.fragment}"

        test = re.compile(pattern)
        if test.match(context_str):
            return ref

    raise ValueError(f"@odata.context not found: {context}")


def fix_schema_inheritance(schema: dict):
    of_keys = ("allOf", "anyOf", "oneOf")

    for k in of_keys:
        insert_items = schema.pop(k, [])
        if insert_items:
            for elem in insert_items:
                properties = elem.get("properties", {})
                if properties:
                    schema["properties"] = {**schema["properties"], **properties}

                for of_key in of_keys:
                    insert_more_items = elem.get(of_key, [])
                    for item in insert_more_items:
                        more_properties = item.get("properties", {})
                        schema["properties"] = {
                            **schema["properties"],
                            **more_properties,
                        }

    return schema


def convert_complex_types_to_string(schema: dict):
    of_keys = ("allOf", "anyOf", "oneOf")
    replacement = {"type": ["string", "null"]}

    properties = schema.get("properties", {})
    new_properties = properties.copy()

    for field_name, field_val in properties.items():
        field_keys = properties.get(field_name, {}).keys()

        has_of_list = any(k for k in field_keys if k in of_keys)
        has_structure = field_val.get("type", {}) in ("array", "object")

        if has_structure or has_of_list:
            new_properties[field_name] = replacement

    return {"type": "object", "properties": new_properties}


def get_schema(context: str) -> dict:
    ref = get_ref(context)

    value = ref.get("properties", {}).get("value", {}).get("items", {})
    allOf = ref.get("allOf", [])
    full_schema = value or allOf[0]

    # Singer formatting
    fixed_schema = fix_schema_inheritance(full_schema)
    schema = convert_complex_types_to_string(fixed_schema)

    sorted_properties = sorted(schema.get("properties", {}).items())
    schema["properties"] = dict(sorted_properties)

    return schema


def dump_schema(context: str):
    schema = get_schema(context)

    link = urlsplit(context)
    version = link.path.split("/")[1]

    file_name = link.fragment.split("(")[0]
    schema_fp = f"tap_ms_graph/schemas/{version}/{file_name}.json"

    with open(schema_fp, "w") as fp:
        jsonref.dump(schema, fp, indent=2)
