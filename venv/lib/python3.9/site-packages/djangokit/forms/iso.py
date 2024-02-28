#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from datetime import datetime
from django import forms
from django.forms.utils import from_current_timezone
from django.utils.dateparse import parse_datetime


class IsoDateTimeField(forms.DateTimeField):
    """DateTimeField with support ISO format."""

    def prepare_value(self, value):
        if isinstance(value, datetime):
            value = value.isoformat()
        return value

    def to_python(self, value):
        # First parse from ISO format.
        if value and isinstance(value, str):
            result = parse_datetime(value)
            if result:
                return from_current_timezone(result)
        # If not ISO format then standard behavior.
        return super().to_python(value)
