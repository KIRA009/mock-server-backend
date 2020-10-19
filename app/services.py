import re

from .models import BaseEndpoint, RelativeEndpoint, Schema, SchemaData, Field, PrimitiveDataType
from utils.exceptions import AccessDenied


def base_endpoint_add(data):
	if not data['endpoint'].startswith('/'):
		data['endpoint'] = '/' + data['endpoint']
	endpoint = BaseEndpoint.objects.get_or_create(endpoint=data['endpoint'])
	return endpoint


def relative_endpoint_add(data):
	methods = [k[0] for k in RelativeEndpoint.METHODS]
	if data['method'] not in methods:
		raise AccessDenied(f"Please enter valid method, i.e. one of {', '.join(methods)}")
	if not data['endpoint'].startswith('/'):
		data['endpoint'] = '/' + data['endpoint']
	if not data['endpoint'].endswith('/'):
		data['endpoint'] += '/'
	data['regex_endpoint'] = data['endpoint']
	pat = re.compile(r':(.*?)/')
	for url_param in pat.findall(data['endpoint']):
		data['regex_endpoint'] = data['regex_endpoint'].replace(f':{url_param}', f'<{url_param}>')
	if RelativeEndpoint.objects.filter(
			base_endpoint_id=data['id'], endpoint=data['endpoint'], method=data['method']
	).exists():
		raise AccessDenied("Endpoint with same method already exists")
	relative_endpoint = RelativeEndpoint.objects.create(
		base_endpoint_id=data['id'], endpoint=data['endpoint'], method=data['method'],
		regex_endpoint=data['regex_endpoint']
	)
	return relative_endpoint


def schema_add(data):
	if Schema.objects.filter(name=data['name']).exists():
		raise AccessDenied(f"{data['name']} schema already exists")
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


def endpoint_update(data):
	new_fields = []
	endpoint = RelativeEndpoint.objects.get(id=data['id'])
	endpoint.fields.exclude(
		id__in=[field['id'] for field in data['fields'] if 'id' in field and field['id'] > 0]
	).delete()  # delete fields which are no longer needed
	fields_to_change = []  # contains fields which need to be changed
	available_url_params = endpoint.url_params  # available url parameters
	schemas = list(Schema.objects.all().values_list('name', flat=True))  # available schemas
	for field in data['fields']:
		if 'isChanged' not in field:
			continue
		if field['type'] == Field.SCHEMA:
			if field['value'] not in schemas:  # check if that data type is acceptable
				raise AccessDenied(
					f"Please enter valid schema name for '{field['key']}', i.e. one of "
					f"{', '.join(schemas)}"
				)
		elif field['type'] == Field.VALUE:
			if field['value'] not in PrimitiveDataType.CHOICES:  # check if that data type is acceptable
				raise AccessDenied(
					f"Please enter valid data type for '{field['key']}', i.e. one of "
					f"{', '.join(PrimitiveDataType.CHOICES)}"
				)
		elif field['type'] == Field.URL_PARAM:
			if field['value'] not in available_url_params:
				raise AccessDenied(
					f"Please enter valid url param for '{field['key']}', i.e. one of "
					f"{', '.join(available_url_params)}"
				)
		elif field['type'] == Field.QUERY_PARAM:
			if not field['value']:
				raise AccessDenied(f"Please enter valid string for '{field['key']}")
		else:
			raise AccessDenied(f'The field type should be one of {Field.SCHEMA}, {Field.VALUE}, {Field.URL_PARAM}')
		if field['isChanged']:  # old fields
			fields_to_change.append(field)
		else:  # new fields
			new_fields.append(field)
	for field in fields_to_change:
		Field.objects.filter(id=field['id']).update(
			key=field['key'], value=field['value'], type=field['type'], is_array=field['is_array']
		)
	Field.objects.bulk_create(
		[
			Field(
				key=field['key'], value=field['value'], type=field['type'], relative_endpoint_id=data['id'],
				is_array=field['is_array']
			) for field in new_fields
		]
	)
	endpoint.meta_data = data['meta_data']
	endpoint.save()
	return endpoint
