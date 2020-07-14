from django.db import models
import json

from utils.model_mixin import AutoCreatedUpdatedMixin


class BaseEndpoint(AutoCreatedUpdatedMixin):
	endpoint = models.TextField(blank=True, default='')


class RelativeEndpoint(AutoCreatedUpdatedMixin):
	GET = 'GET'
	POST = 'POST'
	PUT = 'PUT'
	METHODS = (
		(GET, GET),
		(POST, POST),
		(PUT, PUT)
	)
	base_endpoint = models.ForeignKey(BaseEndpoint, on_delete=models.CASCADE, related_name='relative_endpoints')
	endpoint = models.TextField(blank=True, default='')
	schema = models.TextField(default='{}')
	method = models.TextField(max_length=4, choices=METHODS)
	is_paginated = models.BooleanField(default=False)
	records_per_page = models.IntegerField(default=1)
	total_pages = models.IntegerField(default=1)

	process_fields = AutoCreatedUpdatedMixin.get_process_fields_copy()
	process_fields.update(**dict(
		schema=lambda x: json.loads(x)
	))

	def save(self):
		if isinstance(self.schema, dict):
			self.schema = json.dumps(self.schema)
		super().save()


class Schema(AutoCreatedUpdatedMixin):
	name = models.TextField(blank=False, null=False)

	def resolve_schema(self, data):
		if data.is_value_primitive:
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
	exclude_fields = AutoCreatedUpdatedMixin.get_exclude_fields_copy()
	exclude_fields += ['id']
	process_fields.update(**dict(
		schema=lambda x: x.get_schema()
	))


class SchemaData(AutoCreatedUpdatedMixin):
	schema = models.ForeignKey(Schema, on_delete=models.CASCADE, related_name='schema_data')
	key = models.CharField(max_length=255)
	value = models.IntegerField()
	is_value_primitive = models.BooleanField(default=True)


class PrimitiveDataType:
	STRING = 'string'
	NUMBER = 'number'
	BOOLEAN = 'boolean'
	CHOICES = [STRING, NUMBER, BOOLEAN]
