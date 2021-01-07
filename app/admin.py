from django.contrib import admin

from .models import *

for model in [RelativeEndpoint, BaseEndpoint, Field, Schema]:
    admin.site.register(model)
