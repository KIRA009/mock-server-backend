from app.models import Schema

from .fakers import get_random_value
import json

class Response:
    def __init__(self, fields, meta_data, page_no):
        self.fields = fields
        self.meta_data = json.loads(meta_data)
        # NOTE: hardcoded for testing
        self.meta_data['records_per_page'] = 5
        self.meta_data['num_records'] = 13
        self.page_no = int(page_no)
        self.cache = dict()  # maybe used for caching results
        self.mapping = dict(
            value=self._value_field,
            schema=self._schema_field
        )

    def get_data(self, count):
        data = list()

        for _ in range(count):
            page = dict()
            for field in self.fields:
                page[field.key] = self.mapping[field.type](field)
            data.append(page)

        return data

    def create_response(self):
        response = dict()
        response['items'] = list()

        if self.meta_data['is_paginated']:
            response['page_no'] = self.page_no
            response['total_pages'] = (int)(self.meta_data['num_records'] / self.meta_data['records_per_page'])
            
            if (self.meta_data['num_records'] % self.meta_data['records_per_page']) != 0:
                response['total_pages'] += 1
            
            if self.page_no > response['total_pages'] or self.page_no < 1:
                return {}

            response['items'] = \
                    self.get_data( \
                        min(self.meta_data['num_records'] - (self.page_no - 1) * self.meta_data['records_per_page'], \
                        self.meta_data['records_per_page']) \
                    )
        else:
            response['items'] = self.get_data(self.meta_data['num_records'])

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
