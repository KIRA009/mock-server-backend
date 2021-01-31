from django.contrib import admin

from .models import *

for model in [RelativeEndpoint, BaseEndpoint, Field, Schema, StatusCode, SchemaData]:
    admin.site.register(model)
