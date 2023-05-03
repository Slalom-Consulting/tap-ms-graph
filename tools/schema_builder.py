import json
import re

import lxml.etree as ET
import requests
import jsonref

API_VERSION = "v1.0"

xml_link = f"https://graph.microsoft.com/{API_VERSION}/$metadata"
xsl_link = "https://raw.githubusercontent.com/oasis-tcs/odata-json-schema/main/tools/V4-CSDL-to-JSONSchema.xsl"


def get_dom_doc() -> dict:
    xml_file = requests.get(xml_link).content
    xsl_file = requests.get(xsl_link).content

    dom = ET.fromstring(xml_file)
    xslt = ET.fromstring(xsl_file)
    transform = ET.XSLT(xslt)
    newdom = transform(dom)
    dom_json = str(newdom)
    return json.loads(dom_json)


def get_refs(dom_doc, odata_context:str):
    val = odata_context.lstrip(f"https://graph.microsoft.com/{API_VERSION}/")

    contexts = dom_doc.get('anyOf')
    for context in contexts:
        properties = context.get("properties")

        pattern = re.compile(properties.get("@odata.context").get("pattern"))
        if pattern.match(val):
            print(f'Using schema "{context.get("description")}"')
            
            refs = context.get("allOf")

            val = properties.get("value")
            if val:
                refs = [val.get("items")]

            return [ref.get('$ref') for ref in refs]
        # return [ref.get('$ref').lstrip("#/definitions/") for ref in refs]
                

def get_schema(dom_doc, odata_context:str):
    definitions = json.dumps({"definitions": dom_doc.get("definitions")})
    fixed = definitions.replace(
        "https://oasis-tcs.github.io/odata-json-schema/tools/odata-meta-schema.json",
        "https://raw.githubusercontent.com/oasis-tcs/odata-json-schema/main/tools/odata-meta-schema.json"
    )

    full_schema = jsonref.loads(fixed)

    ref = get_refs(dom_doc, odata_context)[0]
    schema = full_schema.get("definitions").get(ref)

    return {
        "type": schema.get("type"),
        "properties": schema.get("properties")
    }


dom_doc = get_dom_doc()
odata_context = "https://graph.microsoft.com/v1.0/$metadata#users"


schema = get_schema(dom_doc, odata_context)

with open("test.json", "w") as fp:
    json.dump(get_schema(dom_doc, odata_context), fp, indent=2)
    #json.dump(test3, fp, indent=2)



dom_doc = get_dom_doc()


odata_context = "https://graph.microsoft.com/v1.0/$metadata#users"
test = get_refs(dom_doc, odata_context)

definitions = json.dumps({"definitions": dom_doc.get("definitions")})
fixed = definitions.replace("https://oasis-tcs.github.io/odata-json-schema/tools/odata-meta-schema.json", "https://raw.githubusercontent.com/oasis-tcs/odata-json-schema/main/tools/odata-meta-schema.json")

test2 = jsonref.loads(fixed)

test3 = test2.get("definitions").get(test[0])

test3.get("properties").keys()


#with open("t.json", 'w') as f:
#    json.dump(definitions, f, indent=4)



