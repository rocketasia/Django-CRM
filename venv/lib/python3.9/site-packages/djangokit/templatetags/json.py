#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the same license as the current project.
#
from django import template
from djangokit.utils.encoders import dump_to_json

register = template.Library()


@register.filter
def jsondumps(data, indent=None):
    if data is None:
        return ''
    return dump_to_json(data, indent=indent)


@register.filter
def jsondumps_unicode(data, indent=None):
    if data is None:
        return ''
    return dump_to_json(data, indent=indent, ensure_ascii=False)
