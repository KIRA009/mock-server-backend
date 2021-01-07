from django.urls import path

from .views import *

urlpatterns = list(
	map(lambda x: path(x[0], x[1]), [
		('', check_server_status),
		('base-endpoints/get/', get_base_endpoints),
		('base-endpoint/add/', add_base_endpoint),
		('relative-endpoints/get/<int:base_endpoint_id>/', get_relative_endpoints),
		('relative-endpoints/add/', add_relative_endpoint),
		('schemas/get/', get_schemas),
		('schema/add/', add_schema),
		('update_schema/', update_endpoint_schema),
		('relative-endpoint/update/', update_relative_endpoint),
		('relative-endpoint/delete/', delete_relative_endpoint),
		('data/export/', export_data),
		('data/import/', import_data),
	])
)
