#
# Copyright (c) 2018, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
try:
    from django.db.models import JSONField as BaseJSONField
except ImportError:
    from django.contrib.postgres.fields.jsonb import JSONField as BaseJSONField
from djangokit.forms.postgres import JSONField as FormJSONField
from djangokit.utils.encoders import JSONEncoder


class JSONField(BaseJSONField):
    """Django PostgreSQL JSONField with custom encoder."""

    def __init__(self, *args, **kwargs):
        super(JSONField, self).__init__(*args, **kwargs)
        if not self.encoder:
            self.encoder = JSONEncoder

    def formfield(self, **kwargs):
        return super().formfield(**{
            'form_class': FormJSONField,
            **kwargs,
        })
