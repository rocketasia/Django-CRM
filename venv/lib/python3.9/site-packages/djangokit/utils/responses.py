#
# Copyright (c) 2017, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from django.http import JsonResponse as BaseJsonResponse
from django.utils.timezone import now

from djangokit.utils.encoders import JSONEncoder


class JsonResponse(BaseJsonResponse):
    def __init__(self, data, **kwargs):
        kwargs.setdefault('encoder', JSONEncoder)
        BaseJsonResponse.__init__(self, data, **kwargs)


class BaseApi(object):
    """Базовый класс для обработки запросов из Node.js."""

    def test(self, request, **kwargs):
        data = {'time': now()}
        data.update(kwargs)
        return data
