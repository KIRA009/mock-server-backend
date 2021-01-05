from django.http import JsonResponse
from django.db.models.functions import Concat
from django.urls.resolvers import RegexPattern

from app.models import RelativeEndpoint
from utils.queryset import query_debugger
from utils.exceptions import NotFound
from .utils import Response


# @query_debugger
def abc(request, route):
    endpoints = RelativeEndpoint.objects.annotate(
        final_endpoint=Concat('base_endpoint__endpoint', 'regex_endpoint')).all()
    endpoint = None
    for _route in endpoints:
        f = RegexPattern('^' + _route.final_endpoint + '$')
        if f.match(route) is not None:
            endpoint = _route
            break
    if endpoint is None:
        raise NotFound('Matching api endpoint not found')
    response = Response(endpoint.fields.all())
    return JsonResponse(response.create_response())
