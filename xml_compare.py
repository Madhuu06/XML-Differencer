import xml.etree.ElementTree as ET

def strip_ns(tag):
    return tag.split('}', 1)[-1] if '}' in tag else tag

# Optionally extend these for alias mapping
TAG_MAPPING = {}
ATTR_MAPPING = {}

IGNORE_TAGS = {
    "ApplicationArea", "Process", "ActionCriteria", "ActionExpression",
}

def canonical_tag(local):
    return TAG_MAPPING.get(local, local)

def canonical_attr(local):
    return ATTR_MAPPING.get(local, local)

def parse_xml_from_string(xml_string):
    try:
        root = ET.fromstring(xml_string)
        return root, None
    except ET.ParseError as e:
        return None, f"XML ParseError: {e}"

def flatten_elements(root: ET.Element) -> dict:
    elements = {}

    def recurse(elem: ET.Element, path="", sib_counter=None):
        if sib_counter is None:
            sib_counter = {}

        local = strip_ns(elem.tag)
        canon = canonical_tag(local)

        if canon in IGNORE_TAGS:
            return

        attribs = {canonical_attr(strip_ns(k)): v for k, v in elem.attrib.items()}
        name_attr = attribs.get("name")

        if canon in {"ProtocolData", "UserDataField"} and name_attr:
            new_path = f"{path}/{canon}[@name='{name_attr}']"
        else:
            idx = sib_counter.get(canon, 0) + 1
            sib_counter[canon] = idx
            new_path = f"{path}/{canon}[{idx}]" if path else f"/{canon}[{idx}]"

        elements[new_path] = {
            "attrib": attribs,
            "text": (elem.text or "").strip()
        }

        child_counts = {}
        for child in elem:
            recurse(child, new_path, child_counts)

    recurse(root)
    return elements

def compare_xml(wcs_dict: dict, micro_dict: dict):
    diffs = []

    for path, wcs_elem in wcs_dict.items():
        if path not in micro_dict:
            diffs.append({
                "Difference Type": "Tag missing",
                "Tag Path": path,
                "Attribute": "-"
            })
            continue

        micro_elem = micro_dict[path]

        for attr, wcs_val in wcs_elem["attrib"].items():
            mic_val = micro_elem["attrib"].get(attr)
            if mic_val is None:
                diffs.append({
                    "Difference Type": "Attribute missing",
                    "Tag Path": path,
                    "Attribute": attr
                })
            elif mic_val != wcs_val:
                diffs.append({
                    "Difference Type": "Attribute mismatch",
                    "Tag Path": path,
                    "Attribute": attr
                })

        if wcs_elem["text"] != micro_elem["text"]:
            diffs.append({
                "Difference Type": "Text mismatch",
                "Tag Path": path,
                "Attribute": "(text)"
            })

    for path in micro_dict:
        if path not in wcs_dict:
            diffs.append({
                "Difference Type": "Extra tag",
                "Tag Path": path,
                "Attribute": "-"
            })

    return diffs
