import json
import re
from typing import Dict

import jsonref
import lxml.etree as ET
import requests
from memoization import cached

API_VERSION = "v1.0"

xml_link = f"https://graph.microsoft.com/{API_VERSION}/$metadata"
xsl_link = "https://raw.githubusercontent.com/oasis-tcs/odata-json-schema/main/tools/V4-CSDL-to-JSONSchema.xsl"
odata_meta_schema = "https://raw.githubusercontent.com/oasis-tcs/odata-json-schema/main/tools/odata-meta-schema.json"


@cached
def get_dom_doc() -> dict:
    xml_file = requests.get(xml_link).content
    xsl_file = requests.get(xsl_link).content

    dom = ET.fromstring(xml_file)
    xslt = ET.fromstring(xsl_file)
    transform = ET.XSLT(xslt)
    newdom = transform(dom)
    dom_json = str(newdom)

    dom_json_fixed = dom_json.replace(
        "https://oasis-tcs.github.io/odata-json-schema/tools/odata-meta-schema.json",
        odata_meta_schema,
    )

    return json.loads(dom_json_fixed)


def get_refs(dom_doc: dict, odata_context: str) -> list:
    base_url = f"https://graph.microsoft.com/{API_VERSION}/"
    val = odata_context.lstrip(base_url)

    contexts: Dict[dict] = dom_doc.get("anyOf", {})
    for c in contexts:
        properties = c.get("properties", {})

        pattern = re.compile(properties.get("@odata.context", {}).get("pattern", ""))
        if pattern.match(val):
            context = c
            break

    if not context:
        return

    description = context.get("description", "")
    print(f'Using schema "{description}"')

    refs_doc: Dict[dict] = context.get("allOf", {})

    value = properties.get("value", {})
    if value:
        refs_doc = [value.get("items")]

    return [ref.get("$ref", "") for ref in refs_doc]


def get_schema(dom_doc: dict, odata_context: str) -> dict:
    context_refs = get_refs(dom_doc, odata_context)
    context_ref = context_refs[0]

    definitions = json.dumps(
        {"context": {"$ref": context_ref}, "definitions": dom_doc.get("definitions")}
    )

    full_schema = jsonref.loads(definitions)
    context_schema = full_schema.get("context", {})

    return {
        "type": context_schema.get("type"),
        "properties": context_schema.get("properties"),
    }


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


def save_schema_doc(odata_context: str):
    dom_doc = get_dom_doc()
    schema = get_schema(dom_doc, odata_context)
    clean_schema = convert_complex_types_to_string(schema)

    stream_name = odata_context.split("#")[-1]
    schema_fp = f"tap_ms_graph/schemas/{API_VERSION}/{stream_name}.json"

    with open(schema_fp, "w") as fp:
        json.dump(clean_schema, fp, indent=2)


odata_context = "https://graph.microsoft.com/v1.0/$metadata#subscribedSkus"
save_schema_doc(odata_context)
