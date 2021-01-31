import jsonschema
from collections import ChainMap

from .exceptions import AccessDenied


def create_schema(props):
    required = []
    reqs = []
    for k, v in props.items():
        if isinstance(v, dict):
            if "properties" in v:
                pass
            if "req" in v and v["req"]:
                required.append(k)
            props[k], req = create_schema(v)
            if req:
                reqs += req
    if reqs:
        props["required"] = reqs
    props["additionalProperties"] = False
    return props, required


def validate(*_properties):
    def inner(func):
        def inner2(request, **kwargs):
            if "json" in request.__dict__:
                data = request.json
            else:
                data = request.POST.dict()
            properties = dict(ChainMap(*_properties))
            properties, required = create_schema(properties)

            schema = dict(
                type="object",
                properties=properties,
                required=required,
                additionalProperties=False,
            )
            try:
                jsonschema.validate(data, schema)
                return func(request, **kwargs)
            except jsonschema.exceptions.ValidationError as e:
                path = ""
                for i in e.path:
                    path += f"{i}."
                raise AccessDenied(f"{path}{e.message}")

        return inner2

    return inner


def get_required(is_required):
    return {"req": is_required}


def make_object(x, _type, is_required=True, **kwargs):
    return {x: dict(type=_type, **get_required(is_required), **kwargs)}


def make_string_object(x, is_required=True):
    return make_object(x, "string", is_required)


def make_number_object(x, is_required=True):
    return make_object(x, "number", is_required)


def make_array_object(x, _type, is_required=True, **kwargs):
    return make_object(x, "array", is_required, items=dict(type=_type, **kwargs))


def make_email_object(x, is_required=True):
    return make_object(x, "string", is_required, pattern="^.*@.*\..*$")


def make_uri_object(x, is_required=True):
    return make_object(x, "string", is_required, pattern="^https?://.+")


def make_dict_object(x, is_required=True, **kwargs):
    return make_object(x, "object", is_required, **kwargs)


def make_boolean_object(x, is_required=True, **kwargs):
    return make_object(x, "boolean", is_required, **kwargs)
