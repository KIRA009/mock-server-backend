from django.urls import re_path

from .views import *

urlpatterns = [re_path(r"^(?P<route>(.+\/{1})+)$", abc)]
