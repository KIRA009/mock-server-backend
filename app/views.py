from django.views import View
from django.db import transaction

from .models import BaseEndpoint, RelativeEndpoint, Schema, PrimitiveDataType, SchemaData, Field
from .validators import *
from utils.exceptions import AccessDenied


class ServerStatusView(View):
	def get(self, request):
		return dict()


class BaseEndpointView(View):
	def get_all_base_endpoints(self):
		return dict(baseEndpoints=BaseEndpoint.objects.all().detail())

	def get(self, request):
		return self.get_all_base_endpoints()

	@create_base_endpoint_schema
	def post(self, request):
		data = request.json
		if not data['endpoint'].startswith('/'):
			data['endpoint'] = '/' + data['endpoint']
		endpoint = BaseEndpoint.objects.get_or_create(endpoint=data['endpoint'])
		return dict(id=endpoint.id)


class RelativeEndpointView(View):
	def get_endpoints(self, base_endpoint_id):
		return dict(relativeEndpoints=RelativeEndpoint.objects.filter(base_endpoint_id=base_endpoint_id).detail())

	def get(self, request):
		base_endpoint_id = int(request.GET.get('baseEndpoint'))
		return self.get_endpoints(base_endpoint_id)

	@create_relative_endpoint_schema
	def post(self, request):
		data = request.json
		methods = [k[0] for k in RelativeEndpoint.METHODS]
		if data['method'] not in methods:
			raise AccessDenied(f"Please enter valid method, i.e. one of {', '.join(methods)}")
		if not data['endpoint'].startswith('/'):
			data['endpoint'] = '/' + data['endpoint']
		if RelativeEndpoint.objects.filter(
				base_endpoint_id=data['id'], endpoint=data['endpoint'], method=data['method']
		).exists():
			raise AccessDenied("Endpoint with same method already exists")
		relative_endpoint = RelativeEndpoint(
			base_endpoint_id=data['id'], endpoint=data['endpoint'], method=data['method']
		)
		relative_endpoint.save()
		return dict(id=relative_endpoint.id)


class UpdateSchemaView(View):
	@update_endpoint_schema_schema
	def post(self, request):
		data = request.json
		new_fields = []
		endpoint = RelativeEndpoint.objects.get(id=data['id'])
		endpoint.fields.exclude(
			id__in=[field['id'] for field in data['fields'] if 'id' in field and field['id'] > 0]
		).delete()
		for field in data['fields']:
			if 'isChanged' not in field:
				continue
			if field['isChanged']:
				if field['type'] == 'schema':
					Schema.objects.get(name=field['value'])
				else:
					if field['value'] not in PrimitiveDataType.CHOICES:
						raise AccessDenied(
							f"Please enter valid data type for '{field['key']}', i.e. one of "
							f"{', '.join(PrimitiveDataType.CHOICES)}"
						)
				Field.objects.filter(id=field['id']).update(key=field['key'], value=field['value'], type=field['type'])
			else:
				if field['type'] == 'schema':
					Schema.objects.get(name=field['value'])
				else:
					if field['value'] not in PrimitiveDataType.CHOICES:
						raise AccessDenied(
							f"Please enter valid data type for '{field['key']}', i.e. one of "
							f"{', '.join(PrimitiveDataType.CHOICES)}"
						)
				new_fields.append(field)
		Field.objects.bulk_create(
			[
				Field(
					key=field['key'], value=field['value'], type=field['type'], relative_endpoint_id=data['id']
				) for field in new_fields
			]
		)
		return dict(fields=endpoint.fields.all().detail())


class SchemaView(View):
	def get_schemas(self):
		return dict(schemas=Schema.objects.all().detail())

	def get(self, request):
		return self.get_schemas()

	@create_schema_schema
	def post(self, request):
		data = request.json
		if Schema.objects.filter(name=data['name']).exists():
			raise AccessDenied(f"{data['name']} schema already exists")
		with transaction.atomic():
			schema = Schema.objects.create(name=data['name'])
			schema_datas = []
			for field in data['fields']:
				schema_data = SchemaData(schema=schema, key=field['key'], type=field['type'])
				if field['type'] == 'schema':
					schema_data.value = Schema.objects.get(name=field['value']).id
				else:
					if field['value'] not in PrimitiveDataType.CHOICES:
						raise AccessDenied(
							f"Please enter valid data type, i.e. one of {', '.join(PrimitiveDataType.CHOICES)}"
						)
					schema_data.value = PrimitiveDataType.CHOICES.index(field['value'])
				schema_datas.append(schema_data)
			SchemaData.objects.bulk_create(schema_datas)
		return dict()
