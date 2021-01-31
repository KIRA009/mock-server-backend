import re

from utils.exceptions import NotAllowed
from .models import Field


def format_and_regex_endpoint(endpoint):
    if not endpoint.startswith("/"):
        endpoint = "/" + endpoint
    if not endpoint.endswith("/"):
        endpoint += "/"
    regex_endpoint = endpoint
    pat = re.compile(r":(.*?)/")
    for url_param in pat.findall(endpoint):
        regex_endpoint = regex_endpoint.replace(f":{url_param}", f"<str:{url_param}>")
    return endpoint, regex_endpoint


def verify_and_sort_fields(fields, checkers, available_types, extras=dict()):
    new_fields = []
    fields_to_change = []
    for field in fields:
        if "isChanged" not in field:
            continue
        if field["type"] == Field.POST_DATA:
            if extras["endpoint"].method != "POST":
                raise NotAllowed(f"The endpoint should have a POST method")
        if field["type"] == Field.SCHEMA:
            if "schema_name" in extras:
                if field["value"] == extras["schema_name"]:
                    raise NotAllowed("Schema cannot be a field of itself")
        if field["type"] in checkers:
            if field["value"] not in checkers[field["type"]]:
                raise NotAllowed(
                    f"Please enter valid data for '{field['key']}', i.e. one of "
                    f"{', '.join(checkers[field['type']])}"
                )
        else:
            if field["type"] not in available_types:
                raise NotAllowed(
                    f'The field type should be one of {", ".join(available_types)}'
                )
            if not field["value"]:
                raise NotAllowed(f"Please enter valid data for '{field['key']}")

        if field["isChanged"]:  # old fields
            del field["isChanged"]
            fields_to_change.append(field)
        else:  # new fields
            del field["isChanged"]
            del field["id"]
            new_fields.append(field)
    return new_fields, fields_to_change


def get_machine_readable_field_values(fields, mapping):
    for field in fields:
        field["value"] = mapping[field["type"]](field["value"])

    return fields
