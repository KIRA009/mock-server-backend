from .models import BaseEndpoint, RelativeEndpoint, Schema


def base_endpoints_get():
	return BaseEndpoint.objects.all().detail()


def relative_endpoints_get(base_endpoint_id):
	return RelativeEndpoint.objects.filter(base_endpoint_id=base_endpoint_id).order_by('-created_at').detail()


def schemas_get():
	return Schema.objects.all().detail()
