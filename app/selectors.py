from .models import BaseEndpoint, Field, RelativeEndpoint, Schema, PrimitiveDataType


def base_endpoints_get():
    return BaseEndpoint.objects.all().detail()


def relative_endpoints_get(base_endpoint_id):
    return (
        RelativeEndpoint.objects.filter(base_endpoint_id=base_endpoint_id)
        .order_by("-created_at")
        .detail()
    )


def schemas_get():
    return Schema.objects.all().detail()


def schema_get(name):
    schema = Schema.objects.get(name=name)
    schemas = {_["id"]: _["name"] for _ in schemas_get()}
    fields = schema.schema_data.all().detail()
    for field in fields:
        if field["type"] == Field.SCHEMA:
            field["value"] = schemas[field["value"]]
        else:
            field["value"] = PrimitiveDataType.CHOICES[field["value"]]
    return dict(id=schema.id, name=name, fields=fields)
