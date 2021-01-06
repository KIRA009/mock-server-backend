from app.models import Schema

from .fakers import get_random_value

class Response:
    def __init__(self, fields):
        self.fields = fields
        self.cache = dict()  # maybe used for caching results
        self.mapping = dict(
            value=self._value_field,
            schema=self._schema_field
        )

    def create_response(self):
        response = dict()
        for field in self.fields:
            response[field.key] = self.mapping[field.type](field)

        return response

    def _value_field(self, field):
        return get_random_value(field.key, field.value)

    def _resolve_schema(self, obj):
        for k, v in obj.items():
            if isinstance(v, str):
                obj[k] = get_random_value(k, v)
            else:
                obj[k] = self._resolve_schema(v)
        return obj

    def _schema_field(self, field):
        schema = Schema.objects.get(name=field.value).get_schema()
        return self._resolve_schema(schema)
