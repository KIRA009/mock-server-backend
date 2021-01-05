from django.contrib import admin

from .models import *

for model in [RelativeEndpoint, BaseEndpoint, Field]:
    admin.site.register(model)
