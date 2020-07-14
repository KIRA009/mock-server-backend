from django.db.models import Manager
from .queryset import BaseQuerySet

from .exceptions import NotFound


class BaseManager(Manager.from_queryset(BaseQuerySet)):
    def get_or_create(self, defaults=None, **kwargs):
        try:
            return super().get_or_create(defaults, **kwargs)
        except NotFound:
            return super().create(**kwargs)

    def get(self, **kwargs):
        try:
            return super().get(**kwargs)
        except self.model.DoesNotExist:
            raise NotFound(f'The {self.model._meta.model_name} requested for does not exist')
