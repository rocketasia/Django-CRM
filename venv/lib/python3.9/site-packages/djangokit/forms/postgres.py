#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
try:
    from django.forms import JSONField as BaseJSONField
except ImportError:
    from django.contrib.postgres.forms.jsonb import JSONField as BaseJSONField
from django.utils.translation import gettext_lazy as _
from djangokit.utils.encoders import dump_to_json


class JSONField(BaseJSONField):
    default_error_messages = {
        'invalid': _('Введите правильный JSON.'),
    }

    def prepare_value(self, value):
        if isinstance(value, str):
            return value
        kwargs = {'indent': 2, 'ensure_ascii': False, 'sort_keys': True}
        return dump_to_json(value, **kwargs)
