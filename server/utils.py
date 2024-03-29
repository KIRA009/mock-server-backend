from app.models import Schema, StatusCode
from utils.exceptions import NotAllowed

from .fakers import get_random_value
import json


class Response:
    def __init__(self, fields, meta_data, page_no, url_params, query_params, data):
        self.fields = fields
        self.meta_data = json.loads(meta_data)
        self.page_no = int(page_no)
        self.url_params = url_params
        self.query_params = query_params
        self.cache = dict()  # maybe used for caching results
        self.data = data
        self.mapping = dict(
            value=self._value_field,
            schema=self._schema_field,
            url_param=self._url_param_field,
            query_param=self._query_param_field,
            post_data=self._post_data_field,
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

        if self.meta_data["is_paginated"]:
            response["page_no"] = self.page_no
            response["total_pages"] = (int)(
                self.meta_data["num_records"] / self.meta_data["records_per_page"]
            )

            if (
                self.meta_data["num_records"] % self.meta_data["records_per_page"]
            ) != 0:
                response["total_pages"] += 1

            response["items"] = self.get_data(
                min(
                    self.meta_data["num_records"]
                    - (self.page_no - 1) * self.meta_data["records_per_page"],
                    self.meta_data["records_per_page"],
                )
            )
        else:
            response = self.get_data(1)[0]

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

    def _url_param_field(self, field):
        return self.url_params[field.value]

    def _query_param_field(self, field):
        return self.query_params.get(field.value, get_random_value(field.key, "string"))

    def _post_data_field(self, field):
        if field.value not in self.data:
            raise NotAllowed(f"{field.value} should be present in request body")
        return self.data[field.value]


def get_active_status_code(endpoint):
    return StatusCode.objects.get(
        relative_endpoint=endpoint, status_code=endpoint.active_status_code
    )
