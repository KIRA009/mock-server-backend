import json

from .models import (
    BaseEndpoint,
    RelativeEndpoint,
    Schema,
    SchemaData,
    Field,
    PrimitiveDataType,
    StatusCode,
)
from utils.exceptions import NotAllowed
from .utils import (
    format_and_regex_endpoint,
    verify_and_sort_fields,
    get_machine_readable_field_values,
)


def base_endpoint_add(data):
    if data["endpoint"].startswith("/"):
        data["endpoint"] = data["endpoint"][1:]
    endpoint = BaseEndpoint.objects.get_or_create(endpoint=data["endpoint"])
    return endpoint


def relative_endpoint_add(data):
    methods = [k[0] for k in RelativeEndpoint.METHODS]
    if data["method"] not in methods:
        raise NotAllowed(f"Please enter valid method, i.e. one of {', '.join(methods)}")
    data["endpoint"], data["regex_endpoint"] = format_and_regex_endpoint(
        data["endpoint"]
    )
    if RelativeEndpoint.objects.filter(
        base_endpoint_id=data["id"], endpoint=data["endpoint"], method=data["method"]
    ).exists():
        raise NotAllowed("Endpoint with same method already exists")
    relative_endpoint = RelativeEndpoint.objects.create(
        base_endpoint_id=data["id"],
        endpoint=data["endpoint"],
        method=data["method"],
        regex_endpoint=data["regex_endpoint"],
    )
    StatusCode.objects.create(relative_endpoint=relative_endpoint, status_code=200)
    return relative_endpoint


def schema_add(data):
    if Schema.objects.filter(name=data["name"]).exists():
        raise NotAllowed(f"{data['name']} schema already exists")
    schema = Schema.objects.create(name=data["name"])
    schema_datas = []
    for field in data["fields"]:
        schema_data = SchemaData(schema=schema, key=field["key"], type=field["type"])
        if field["type"] == "schema":
            schema_data.value = Schema.objects.get(name=field["value"]).id
        else:
            if field["value"] not in PrimitiveDataType.CHOICES:
                raise NotAllowed(
                    f"Please enter valid data type, i.e. one of {', '.join(PrimitiveDataType.CHOICES)}"
                )
            schema_data.value = PrimitiveDataType.CHOICES.index(field["value"])
        schema_datas.append(schema_data)
    SchemaData.objects.bulk_create(schema_datas)
    return schema.detail()


def schema_update(data):
    schema = Schema.objects.get(id=data["id"])
    schema.schema_data.exclude(
        id__in=[field["id"] for field in data["fields"] if field["id"] > 0]
    ).delete()  # delete all fields whose keys are not in the fields

    schemas = {
        data["name"]: data["id"] for data in Schema.objects.all().values("name", "id")
    }

    checkers = {Field.SCHEMA: schemas, Field.VALUE: PrimitiveDataType.CHOICES}

    new_fields, fields_to_change = verify_and_sort_fields(
        data["fields"],
        checkers=checkers,
        available_types=[_[0] for _ in Field.TYPES[:2]],
        extras=dict(schema_name=data["name"]),
    )

    mapping = {
        Field.VALUE: lambda x: PrimitiveDataType.CHOICES.index(x),
        Field.SCHEMA: lambda x: schemas[x],
    }

    new_fields = get_machine_readable_field_values(new_fields, mapping=mapping)
    fields_to_change = get_machine_readable_field_values(
        fields_to_change, mapping=mapping
    )

    for field in fields_to_change:
        SchemaData.objects.filter(id=field["id"]).update(**field)
    SchemaData.objects.bulk_create(
        [SchemaData(schema=schema, **field) for field in new_fields]
    )
    return schema.detail()


def endpoint_schema_update(data):
    endpoint = RelativeEndpoint.objects.get(id=data["id"])
    active_status = StatusCode.objects.get(
        relative_endpoint=endpoint, status_code=endpoint.active_status_code
    )
    active_status.fields.exclude(
        id__in=[field["id"] for field in data["fields"] if field["id"] > 0]
    ).delete()  # delete fields which are no longer needed

    available_url_params = endpoint.url_params  # available url parameters
    schemas = list(
        Schema.objects.all().values_list("name", flat=True)
    )  # available schemas

    checkers = {
        Field.SCHEMA: schemas,
        Field.VALUE: PrimitiveDataType.CHOICES,
        Field.URL_PARAM: available_url_params,
    }

    new_fields, fields_to_change = verify_and_sort_fields(
        data["fields"],
        checkers=checkers,
        available_types=[_[0] for _ in Field.TYPES],
        extras=dict(endpoint=endpoint),
    )

    for field in fields_to_change:
        Field.objects.filter(id=field["id"]).update(**field)
    Field.objects.bulk_create(
        [Field(status_code_id=active_status.id, **field) for field in new_fields]
    )
    active_status.meta_data = data["meta_data"]
    active_status.headers = data["headers"]
    active_status.save()
    return active_status


def relative_endpoint_update(data):
    relative_endpoint = RelativeEndpoint.objects.select_related("base_endpoint").get(
        id=data["id"]
    )
    data["endpoint"], data["regex_endpoint"] = format_and_regex_endpoint(
        data["endpoint"]
    )
    if RelativeEndpoint.objects.filter(
        base_endpoint=relative_endpoint.base_endpoint_id,
        endpoint=data["endpoint"],
        method=data["method"],
    ).exists():
        raise NotAllowed("Endpoint with same url exists")
    RelativeEndpoint.objects.filter(id=data["id"]).update(
        endpoint=data["endpoint"],
        method=data["method"],
        regex_endpoint=data["regex_endpoint"],
    )


def status_code_update(data):
    relative_endpoint = RelativeEndpoint.objects.get(id=data["id"])
    status_code = StatusCode.objects.get(status_code=relative_endpoint.active_status_code, relative_endpoint_id=data['id'])
    try:
        if len(data['status_code']) != 3:
            raise ValueError
        data['status_code'] = int(data['status_code'])
        if not (100 <= data['status_code'] <= 999):
            raise NotAllowed("Status code should be between 100 and 999 ")

        if StatusCode.objects.filter(status_code=data['status_code'], relative_endpoint_id=data['id']).exists():
            raise NotAllowed("Cannot have two responses with same status code")
        status_code.status_code = data['status_code']
        status_code.save()
        relative_endpoint.active_status_code = data['status_code']
        relative_endpoint.save()
    except ValueError:
        raise NotAllowed("Status code should be a 3 digit number")


def status_code_set(data):
    relative_endpoint = RelativeEndpoint.objects.get(id=data["id"])
    if not StatusCode.objects.filter(status_code=data['status_code'], relative_endpoint_id=data['id']).exists():
        raise NotAllowed("The new status code doesn't exist")
    relative_endpoint.active_status_code = data['status_code']
    relative_endpoint.save()


def status_code_add(data):
    relative_endpoint = RelativeEndpoint.objects.get(id=data["id"])
    try:
        if len(data['status_code']) != 3:
            raise ValueError
        data['status_code'] = int(data['status_code'])
        if not (100 <= data['status_code'] <= 999):
            raise NotAllowed("Status code should be between 100 and 999 ")
        if StatusCode.objects.filter(status_code=data['status_code'], relative_endpoint_id=data['id']).exists():
            raise NotAllowed("Cannot have two responses with same status code")
        status_code = StatusCode.objects.create(relative_endpoint_id=data['id'], status_code=data['status_code'])
        relative_endpoint.active_status_code = data['status_code']
        relative_endpoint.save()
        return status_code.detail()
    except ValueError:
        raise NotAllowed("Status code should be a 3 digit number")


def status_code_delete(data):
    relative_endpoint = RelativeEndpoint.objects.get(id=data["id"])
    if relative_endpoint.status_codes.count() == 1:
        raise NotAllowed("Cannot have endpoint with no status code")
    StatusCode.objects.get(status_code=data['status_code'], relative_endpoint_id=data['id']).delete()
    relative_endpoint.active_status_code = StatusCode.objects.filter(relative_endpoint_id=data['id']).first().status_code
    relative_endpoint.save()
    return relative_endpoint.active_status_code


def relative_endpoint_delete(data):
    RelativeEndpoint.objects.filter(id=data["id"]).delete()


def data_export():
    response = dict()
    response["base_endpoints"] = BaseEndpoint.objects.all().detail()
    response["relative_endpoints"] = RelativeEndpoint.objects.all().detail()
    response["schema"] = Schema.objects.all().detail()
    response["fields"] = Field.objects.all().detail()
    response["schema_data"] = SchemaData.objects.all().detail()
    return response


def data_import(data):
    for model in [BaseEndpoint, RelativeEndpoint, Field, Schema, SchemaData]:
        model.objects.all().delete()

    base_endpoints = [BaseEndpoint(**endpoint) for endpoint in data["base_endpoints"]]
    BaseEndpoint.objects.bulk_create(base_endpoints)

    relative_endpoints = []
    fields = []
    for endpoint in data["relative_endpoints"]:
        for field in endpoint["fields"]:
            field["relative_endpoint_id"] = endpoint["id"]
            fields.append(field)
        del endpoint["fields"]
        del endpoint["url_params"]
        endpoint["base_endpoint_id"] = endpoint["base_endpoint"]
        del endpoint["base_endpoint"]
        endpoint["meta_data"] = json.dumps(endpoint["meta_data"])

        relative_endpoints.append(RelativeEndpoint(**endpoint))
    RelativeEndpoint.objects.bulk_create(relative_endpoints)
    Field.objects.bulk_create([Field(**field) for field in fields])

    schemas = []
    for schema in data["schema"]:
        del schema["schema"]
        schemas.append(Schema(**schema))
    Schema.objects.bulk_create(schemas)

    for schema_data in data["schema_data"]:
        schema_data["schema_id"] = schema_data["schema"]
        del schema_data["schema"]
    schema_datas = [SchemaData(**schema_data) for schema_data in data["schema_data"]]
    SchemaData.objects.bulk_create(schema_datas)
