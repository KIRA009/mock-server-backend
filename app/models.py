from django.db import models
import json
import re

from utils.model_mixin import AutoCreatedUpdatedMixin


class BaseEndpoint(AutoCreatedUpdatedMixin):
    endpoint = models.TextField(blank=True, default="")


class RelativeEndpoint(AutoCreatedUpdatedMixin):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    METHODS = ((GET, GET), (POST, POST), (PUT, PUT))
    base_endpoint = models.ForeignKey(
        BaseEndpoint, on_delete=models.CASCADE, related_name="relative_endpoints"
    )
    regex_endpoint = models.TextField(blank=True, default="")
    endpoint = models.TextField(blank=True, default="")
    method = models.TextField(max_length=4, choices=METHODS)
    active_status_code = models.PositiveIntegerField(default=200)

    @property
    def url_params(self):
        pat = re.compile(r"<str:(.*?)>")
        return pat.findall(self.regex_endpoint)

    process_fields = AutoCreatedUpdatedMixin.get_process_fields_copy()
    process_fields.update(
        **dict(
            status_codes=lambda x: x.status_codes.detail(),
            url_params=lambda x: x.url_params,
        )
    )


class StatusCode(AutoCreatedUpdatedMixin):
    relative_endpoint = models.ForeignKey(
        RelativeEndpoint, on_delete=models.CASCADE, related_name="status_codes"
    )
    status_code = models.PositiveIntegerField(default=200)
    meta_data = models.TextField(
        blank=True,
        default='{"num_records": 1, "is_paginated": false, "records_per_page": 1}',
    )
    headers = models.TextField(blank=True, default="[]")

    def save(self, *args, **kwargs):
        if isinstance(self.meta_data, dict):
            self.meta_data = json.dumps(self.meta_data)
        if isinstance(self.headers, list):
            self.headers = json.dumps(
                [
                    dict(key=header["key"], value=header["value"])
                    for header in self.headers
                ]
            )
        super().save(*args, **kwargs)

    @property
    def _headers(self):
        return json.loads(self.headers)

    exclude_fields = AutoCreatedUpdatedMixin.get_exclude_fields_copy()
    exclude_fields += ["relative_endpoint"]

    process_fields = AutoCreatedUpdatedMixin.get_process_fields_copy()
    process_fields.update(
        **dict(
            fields=lambda x: x.fields.detail(),
            meta_data=lambda x: json.loads(x),
            headers=lambda x: json.loads(x),
        )
    )


class Schema(AutoCreatedUpdatedMixin):
    name = models.TextField(blank=False, null=False)

    def resolve_schema(self, data):
        if data.type == Field.VALUE:
            return PrimitiveDataType.CHOICES[data.value]
        schema = dict()
        for _data in Schema.objects.get(id=data.value).schema_data.all():
            schema[_data.key] = self.resolve_schema(_data)
        return schema

    def get_schema(self):
        schema = dict()
        for data in self.schema_data.all():
            schema[data.key] = self.resolve_schema(data)
        return schema

    process_fields = AutoCreatedUpdatedMixin.get_process_fields_copy()
    process_fields.update(**dict(schema=lambda x: x.get_schema()))


class PrimitiveDataType:
    CHOICES = ["string", "number", "boolean"]


class Field(AutoCreatedUpdatedMixin):
    VALUE = "value"
    SCHEMA = "schema"
    URL_PARAM = "url_param"
    QUERY_PARAM = "query_param"
    POST_DATA = "post_data"
    TYPES = (
        (VALUE, VALUE),
        (SCHEMA, SCHEMA),
        (URL_PARAM, URL_PARAM),
        (QUERY_PARAM, QUERY_PARAM),
        (POST_DATA, POST_DATA),
    )
    status_code = models.ForeignKey(
        StatusCode, on_delete=models.CASCADE, related_name="fields"
    )
    key = models.CharField(null=False, max_length=255)
    type = models.TextField(choices=TYPES, null=False)
    value = models.CharField(null=False, max_length=255)
    is_array = models.BooleanField(default=False)

    exclude_fields = AutoCreatedUpdatedMixin.get_exclude_fields_copy()
    exclude_fields += ["status_code"]


class SchemaData(AutoCreatedUpdatedMixin):
    schema = models.ForeignKey(
        Schema, on_delete=models.CASCADE, related_name="schema_data"
    )
    key = models.CharField(max_length=255)
    value = models.IntegerField()
    type = models.TextField(choices=Field.TYPES[:2], null=False)
    is_array = models.BooleanField(default=False)

    exclude_fields = AutoCreatedUpdatedMixin.get_exclude_fields_copy()
    exclude_fields += ["schema"]
