from .models import BaseEndpoint, RelativeEndpoint, Schema, SchemaData, Field, PrimitiveDataType
from utils.exceptions import AccessDenied, NotAllowed
from .utils import format_and_regex_endpoint


def base_endpoint_add(data):
	if not data['endpoint'].startswith('/'):
		data['endpoint'] = '/' + data['endpoint']
	endpoint = BaseEndpoint.objects.get_or_create(endpoint=data['endpoint'])
	return endpoint


def relative_endpoint_add(data):
	methods = [k[0] for k in RelativeEndpoint.METHODS]
	if data['method'] not in methods:
		raise NotAllowed(f"Please enter valid method, i.e. one of {', '.join(methods)}")
	data['endpoint'], data['regex_endpoint'] = format_and_regex_endpoint(data['endpoint'])
	if RelativeEndpoint.objects.filter(
			base_endpoint_id=data['id'], endpoint=data['endpoint'], method=data['method']
	).exists():
		raise NotAllowed("Endpoint with same method already exists")
	relative_endpoint = RelativeEndpoint.objects.create(
		base_endpoint_id=data['id'], endpoint=data['endpoint'], method=data['method'],
		regex_endpoint=data['regex_endpoint']
	)
	return relative_endpoint


def schema_add(data):
	if Schema.objects.filter(name=data['name']).exists():
		raise NotAllowed(f"{data['name']} schema already exists")
	schema = Schema.objects.create(name=data['name'])
	schema_datas = []
	for field in data['fields']:
		schema_data = SchemaData(schema=schema, key=field['key'], type=field['type'])
		if field['type'] == 'schema':
			schema_data.value = Schema.objects.get(name=field['value']).id
		else:
			if field['value'] not in PrimitiveDataType.CHOICES:
				raise NotAllowed(
					f"Please enter valid data type, i.e. one of {', '.join(PrimitiveDataType.CHOICES)}"
				)
			schema_data.value = PrimitiveDataType.CHOICES.index(field['value'])
		schema_datas.append(schema_data)
	SchemaData.objects.bulk_create(schema_datas)


def endpoint_schema_update(data):
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
				raise NotAllowed(
					f"Please enter valid schema name for '{field['key']}', i.e. one of "
					f"{', '.join(schemas)}"
				)
		elif field['type'] == Field.VALUE:
			if field['value'] not in PrimitiveDataType.CHOICES:  # check if that data type is acceptable
				raise NotAllowed(
					f"Please enter valid data type for '{field['key']}', i.e. one of "
					f"{', '.join(PrimitiveDataType.CHOICES)}"
				)
		elif field['type'] == Field.URL_PARAM:
			if field['value'] not in available_url_params:
				raise NotAllowed(
					f"Please enter valid url param for '{field['key']}', i.e. one of "
					f"{', '.join(available_url_params)}"
				)
		elif field['type'] == Field.QUERY_PARAM:
			if not field['value']:
				raise NotAllowed(f"Please enter valid string for '{field['key']}")
		else:
			raise NotAllowed(f'The field type should be one of {Field.SCHEMA}, {Field.VALUE}, {Field.URL_PARAM}')
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


def relative_endpoint_update(data):
	relative_endpoint = RelativeEndpoint.objects.select_related('base_endpoint').get(id=data['id'])
	data['endpoint'], data['regex_endpoint'] = format_and_regex_endpoint(data['endpoint'])
	if RelativeEndpoint.objects.filter(base_endpoint=relative_endpoint.base_endpoint_id, endpoint=data['endpoint'], method=data['method']).exists():
		raise NotAllowed("Endpoint with same url exists")
	RelativeEndpoint.objects.filter(id=data['id']).update(
		endpoint=data['endpoint'], method=data['method'], regex_endpoint=data['regex_endpoint']
	)


def relative_endpoint_delete(data):
	RelativeEndpoint.objects.filter(id=data['id']).delete()
