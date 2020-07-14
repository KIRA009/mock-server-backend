from django.urls import path

from .views import *

urlpatterns = list(
	map(lambda x: path(x[0], x[1].as_view()), [
		('', ServerStatusView),
		('baseEndpoints/', BaseEndpointView),
		('relativeEndpoints/', RelativeEndpointView),
		('schema/', SchemaView)
	])
)