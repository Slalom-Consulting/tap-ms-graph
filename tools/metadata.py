import json
import lxml.etree as ET
import requests

XML_URI = "https://graph.microsoft.com/{version}/$metadata"
XSL_URI = "https://raw.githubusercontent.com/oasis-tcs/odata-json-schema/main/tools/V4-CSDL-to-JSONSchema.xsl"
ODATA_META_SCHEMA_URI = "https://raw.githubusercontent.com/oasis-tcs/odata-json-schema/main/tools/odata-meta-schema.json"
METADATA_FILE = "tap_ms_graph/metadata/{version}.json"

versions = [
    "beta",
    "v1.0"
]


def get_metadata(version:str) -> dict:
    link = XML_URI.format(version=version)
    xml_file = requests.get(link).content
    xsl_file = requests.get(XSL_URI).content

    dom = ET.fromstring(xml_file)
    xslt = ET.fromstring(xsl_file)
    transform = ET.XSLT(xslt)
    newdom = transform(dom)
    dom_json = str(newdom)

    # Fixes broken link
    dom_json_fixed = dom_json.replace(
        "https://oasis-tcs.github.io/odata-json-schema/tools/odata-meta-schema.json",
        ODATA_META_SCHEMA_URI,
    )

    return json.loads(dom_json_fixed)


def dump_metadata(version:str) -> None:
    metadata = get_metadata(version)
    file = METADATA_FILE.format(version=version)

    with open(file, "w") as fp:
        json.dump(metadata, fp, indent=2)


for version in versions:
    dump_metadata(version)
