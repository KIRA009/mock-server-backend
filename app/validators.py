from utils.validators import (
    validate,
    make_string_object,
    make_number_object,
    make_array_object,
    make_boolean_object,
    make_dict_object,
)


create_base_endpoint_schema = validate(make_string_object("endpoint"))

create_relative_endpoint_schema = validate(
    make_number_object("id"),
    make_string_object("endpoint"),
    make_string_object("method"),
)

fields_key = make_array_object(
    "fields",
    _type="object",
    properties=dict(
        **make_number_object("id"),
        **make_string_object("type"),
        **make_string_object("key"),
        **make_string_object("value"),
        **make_boolean_object("is_array"),
        **make_boolean_object("isChanged", is_required=False),
    ),
)

update_endpoint_schema_schema = validate(
    fields_key,
    make_array_object(
        "headers",
        _type="object",
        properties=dict(**make_string_object("key"), **make_string_object("value")),
    ),
    make_number_object("id"),
    make_dict_object(
        "meta_data",
        properties=dict(
            **make_number_object("num_records"),
            **make_boolean_object("is_paginated"),
            **make_number_object("records_per_page"),
        ),
    ),
)

update_status_code_schema = validate(
    make_number_object("id"),
    make_string_object("status_code")
)

create_schema_schema = validate(make_string_object("name"), fields_key)

update_schema_schema = validate(
    make_number_object("id"), make_string_object("name"), fields_key
)

delete_endpoint_schema = validate(make_number_object("id"))
