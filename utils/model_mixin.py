from django.db import models
import django.utils.timezone as tz
import json
from django.core import serializers

from .manager import BaseManager


class AutoCreatedUpdatedMixin(models.Model):
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    exclude_fields = ["created_at", "updated_at"]
    process_fields = {}

    @classmethod
    def get_exclude_fields_copy(cls):
        return cls.exclude_fields.copy()

    @classmethod
    def get_process_fields_copy(cls):
        return cls.process_fields.copy()

    objects = BaseManager()

    class Meta:
        abstract = True
        ordering = ["-created_at"]
        get_latest_by = "created_at"

    def save(self, *args, **kwargs):
        if not self.created_at:
            self.created_at = tz.now() + tz.timedelta(hours=5, minutes=30)
            self.updated_at = self.created_at
        else:
            auto_updated_at_is_disabled = kwargs.pop("disable_auto_updated_at", False)
            if not auto_updated_at_is_disabled:
                self.updated_at = tz.now() + tz.timedelta(hours=5, minutes=30)
        self.full_clean()
        super(AutoCreatedUpdatedMixin, self).save(*args, **kwargs)

    def detail(self):
        ret = json.loads(serializers.serialize("json", [self]))[0]
        ret["fields"]["id"] = ret["pk"]
        for i in self.exclude_fields:
            del ret["fields"][i]
        for k, v in self.process_fields.items():
            ret["fields"][k] = v(ret["fields"].get(k, self))
        return ret["fields"]
