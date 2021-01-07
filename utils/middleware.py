import django.middleware.common as common
import json
from django.http import JsonResponse
import traceback

from mock_server_backend.settings import DEBUG
from .exceptions import AccessDenied


def jsonify(data):
    status_code = int(data.get("status_code", 200))
    if "status_code" in data:
        del data["status_code"]
    return JsonResponse(data, status=status_code, json_dumps_params=dict(indent=4))


class CustomMiddleware(common.CommonMiddleware):
    def process_request(self, request):
        super(CustomMiddleware, self).process_request(request)
        if request.method == "OPTIONS" or "/admin/" in request.path:
            return
        if request.content_type == "application/json":
            if request.body:
                request.json = json.loads(request.body)
            else:
                request.json = dict()

    def process_response(self, request, response):
        if "/admin/" in request.path:
            return super().process_response(request, response)
        if isinstance(response, dict):
            response = jsonify(response)
        else:
            if response.status_code == 404:
                response = jsonify(dict(error="The requested url was not found", status_code=404))
        return super().process_response(request, response)

    def process_exception(self, request, exception):
        if 'status_code' in exception.__dict__:
            return dict(error=exception.message, status_code=exception.status_code)
        if DEBUG:
            print(traceback.format_exc())
            try:
                print(request.json)
            except AttributeError:
                pass
        return dict(error="Server error", status_code=500)
