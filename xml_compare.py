import xml.etree.ElementTree as ET
from collections import defaultdict

def parse_xml_from_string(xml_string):
    try:
        root = ET.fromstring(xml_string)
        return root, None
    except ET.ParseError as e:
        return None, f"XML ParseError: {e}"

def flatten_elements(root):
    elements = {}
    def recurse(element):
        tag = element.tag
        if tag not in elements:
            elements[tag] = []
        elements[tag].append({
            "attrib": element.attrib,
            "text": (element.text or "").strip()
        })
        for child in element:
            recurse(child)
    recurse(root)
    return elements

def compare_xml(good_elements, bad_elements):
    differences = []

    for tag in good_elements:
        good_items = good_elements[tag]
        bad_items = bad_elements.get(tag, [])

        for idx, good_item in enumerate(good_items):
            if idx >= len(bad_items):
                differences.append({
                    "Difference Type": "Tag missing",
                    "Tag Path": tag,
                    "Attribute": "-"
                })
                continue

            bad_item = bad_items[idx]
            good_attribs = good_item['attrib']
            bad_attribs = bad_item['attrib']

            for attr in good_attribs:
                if attr not in bad_attribs:
                    differences.append({
                        "Difference Type": "Attribute missing",
                        "Tag Path": tag,
                        "Attribute": attr
                    })
                elif good_attribs[attr] != bad_attribs[attr]:
                    differences.append({
                        "Difference Type": "Attribute mismatch",
                        "Tag Path": tag,
                        "Attribute": attr
                    })

            if good_item['text'] != bad_item['text']:
                differences.append({
                    "Difference Type": "Text mismatch",
                    "Tag Path": tag,
                    "Attribute": "(text)"
                })

    for tag in bad_elements:
        if tag not in good_elements:
            differences.append({
                "Difference Type": "Extra tag",
                "Tag Path": tag,
                "Attribute": "-"
            })

    return differences