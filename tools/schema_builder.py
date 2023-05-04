import json
import re
from typing import Dict

import jsonref
import lxml.etree as ET
import requests

API_VERSION = "v1.0"

xml_link = f"https://graph.microsoft.com/{API_VERSION}/$metadata"
xsl_link = "https://raw.githubusercontent.com/oasis-tcs/odata-json-schema/main/tools/V4-CSDL-to-JSONSchema.xsl"
odata_meta_schema = "https://raw.githubusercontent.com/oasis-tcs/odata-json-schema/main/tools/odata-meta-schema.json"


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
        odata_meta_schema
    )

    return json.loads(dom_json_fixed)


def get_refs(dom_doc:dict, odata_context:str) -> list:
    base_url = f"https://graph.microsoft.com/{API_VERSION}/"
    val = odata_context.lstrip(base_url)

    contexts:Dict[dict] = dom_doc.get('anyOf', {})
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

    refs_doc:Dict[dict] = context.get("allOf", {})

    value = properties.get("value", {})
    if value:
        refs_doc = [value.get("items")]

    return [ref.get('$ref', "") for ref in refs_doc]
                

def get_schema(dom_doc:dict, odata_context:str):
    #TODO: flatten allOf, anyOf, oneOf from dom_doc.get("definitions")
    #TODO: only get first level
    context_refs = get_refs(dom_doc, odata_context)
    context_ref = context_refs[0]

    definitions = json.dumps({
        "context": {"$ref": context_ref},
        "definitions": dom_doc.get("definitions")
    })

    full_schema = jsonref.loads(definitions)
    context_schema = full_schema.get("context", {})

    return {
        "type": context_schema.get("type"),
        "properties": context_schema.get("properties")
    }



dom_doc = get_dom_doc()
odata_context = "https://graph.microsoft.com/v1.0/$metadata#users"
schema = get_schema(dom_doc, odata_context)

with open("test.json", "w") as fp:
    json.dump(schema, fp, indent=2)

