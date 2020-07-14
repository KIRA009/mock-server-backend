from utils.validators import validate, make_string_object, make_number_object, make_array_object


create_base_endpoint_schema = validate(
	make_string_object("endpoint")
)

create_relative_endpoint_schema = validate(
	make_number_object("id"),
	make_string_object("endpoint"),
	make_string_object("method")
)

update_endpoint_schema_schema = validate(
	make_array_object("fields", _type="object", properties=dict(
		**make_string_object("type"),
		**make_string_object("key"),
		**make_string_object("value"),
	)),
	make_number_object("id")
)

create_schema_schema = validate(
	make_string_object("name"),
	make_array_object("fields", _type="object", properties=dict(
		**make_string_object("type"),
		**make_string_object("key"),
		**make_string_object("value"),
	))
)
