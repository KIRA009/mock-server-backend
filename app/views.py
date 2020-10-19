from django.db import transaction
from django.views.decorators.http import require_http_methods

from .validators import *
from .selectors import base_endpoints_get, relative_endpoints_get, schemas_get
from .services import base_endpoint_add, relative_endpoint_add, schema_add, endpoint_update


@require_http_methods(["GET"])
def check_server_status(request):
	return dict()


@require_http_methods(["GET"])
def get_base_endpoints(request):
	return dict(baseEndpoints=base_endpoints_get())


@require_http_methods(["POST"])
@create_base_endpoint_schema
def add_base_endpoint(request):
	data = request.json
	endpoint = base_endpoint_add(data)
	return dict(id=endpoint.id)


@require_http_methods(["GET"])
def get_relative_endpoints(request, base_endpoint_id):
	return dict(relativeEndpoints=relative_endpoints_get(base_endpoint_id))


@require_http_methods(["POST"])
@create_relative_endpoint_schema
def add_relative_endpoint(request):
	data = request.json
	relative_endpoint = relative_endpoint_add(data)
	return dict(
		id=relative_endpoint.id, regex_endpoint=relative_endpoint.regex_endpoint,
		url_params=relative_endpoint.url_params
	)


@require_http_methods(["POST"])
@update_endpoint_schema_schema
def update_schema(request):
	data = request.json
	endpoint = endpoint_update(data)
	return dict(fields=endpoint.fields.all().detail())


@require_http_methods(["GET"])
def get_schemas(request):
	return dict(schemas=schemas_get())


@require_http_methods(["POST"])
@create_schema_schema
@transaction.atomic
def add_schema(request):
	data = request.json
	schema_add(data)
	return dict()
