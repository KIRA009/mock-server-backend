from django.http import JsonResponse
from django.db.models.functions import Concat
from django.urls.resolvers import RegexPattern, _route_to_regex

from app.models import RelativeEndpoint, StatusCode
from utils.queryset import query_debugger
from utils.exceptions import NotFound, NotAllowed
from .utils import Response, get_active_status_code


# @query_debugger
def abc(request, route):
    endpoints = RelativeEndpoint.objects.annotate(
        final_endpoint=Concat("base_endpoint__endpoint", "regex_endpoint")
    ).all()
    endpoint = None
    #   metas = RelativeEndpoint.objects.filter()
    url_params = {}
    for _route in endpoints:
        regex = _route_to_regex(_route.final_endpoint)
        f = RegexPattern(regex[0])
        is_match = f.match(route)
        if is_match is not None:
            url_params = is_match[2]
            endpoint = _route
            break
    if endpoint is None:
        raise NotFound("Matching api endpoint not found")
    if request.method != endpoint.method:
        raise NotAllowed("This method is not allowed")
    data = request.json if endpoint.method == "POST" else dict()
    active_status_code = get_active_status_code(endpoint)
    response = Response(
        active_status_code.fields.all(),
        active_status_code.meta_data,
        request.GET.get("pageNo", "1"),
        url_params,
        request.GET.dict(),
        data,
    )
    resp = JsonResponse(response.create_response())
    for header in active_status_code._headers:
        resp.__setitem__(header["key"], header["value"])
    return resp
