#
# Copyright (c) 2018, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
"""
Вспомогательный функционал для обработки запросов.
"""
import json
from functools import wraps
from io import BytesIO

from django.http.request import QueryDict, MultiValueDict
from django.http.response import HttpResponseBadRequest
from django.http.multipartparser import MultiPartParserError
from django.utils.encoding import force_str
from django.views.decorators.cache import cache_page


def _user_checksum(user):
    if hasattr(user, 'checksum'):
        return user.checksum
    return str(user.pk)


def cache_user_page(timeout):
    """
    Декоратор кэшированных представлений с разделением на пользователей.
    """

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user = request.user
            if user.is_authenticated:
                key_prefix = "_auth_%s_" % _user_checksum(user)
            else:
                key_prefix = "_auth_0_"
            view = cache_page(timeout, key_prefix=key_prefix)(view_func)
            return view(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def _file_parser(request):
    if hasattr(request, '_body'):
        # Use already read data
        data = BytesIO(request._body)
    else:
        data = request
    try:
        _data, _files = request.parse_file_upload(request.META, data)
    except MultiPartParserError:
        # An error occurred while parsing POST data. Since when
        # formatting the error the request handler might access
        # request.POST, set request._post and request._file to prevent
        # attempts to parse POST data again.
        # Mark that an error occurred. This allows request.__repr__ to
        # be explicit about it instead of simply representing an
        # empty POST
        request._mark_post_parse_error()
        raise
    return _data, _files


def _form_parser(request):
    data = QueryDict(request.body, encoding=request._encoding)
    return data, MultiValueDict()


def _json_parser(request):
    try:
        data = json.loads(
            force_str(request.body, encoding=request._encoding or 'utf-8') or
            '{}'
        )
        request.json_data_ready = True
    except ValueError:
        request._mark_post_parse_error()
        raise
    return data, MultiValueDict()


def _blank_parser(request):
    data = QueryDict('', encoding=request._encoding)
    return data, MultiValueDict()


def _get_parser(request):
    content_type = request.META.get('CONTENT_TYPE', '')
    if content_type.startswith('multipart/form-data'):
        return _file_parser
    elif content_type.startswith('application/x-www-form-urlencoded'):
        return _form_parser
    elif content_type.startswith('application/json'):
        return _json_parser
    return _blank_parser


def parse_data(function=None, force_to_dict=False):
    """Декоратор для представлений, использующихся в качестве REST API."""

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            request.json_data_ready = False
            if not hasattr(request, 'data'):
                if request.method == 'GET':
                    request.data = request.GET
                else:
                    if request._read_started and not hasattr(request, '_body'):
                        request._mark_post_parse_error()
                        request.data = {}
                    else:
                        parser = _get_parser(request)
                        request.data, request._files = parser(request)
            if force_to_dict:
                data = request.data
                if not isinstance(data, dict):
                    request.data = data.dict()
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    if function:
        return decorator(function)
    return decorator


def json_required(function=None):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            content_type = request.META.get('CONTENT_TYPE', '')
            if not content_type.startswith('application/json'):
                return HttpResponseBadRequest(
                    'Content type of request must be "application/json".')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    if function:
        return decorator(function)
    return decorator
