#
# Copyright (c) 2018, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from os.path import dirname as _dirname, basename as _basename
from django import template


register = template.Library()


@register.filter
def dirname(path):
    return _dirname(path)


@register.filter
def basename(path):
    return _basename(path)
