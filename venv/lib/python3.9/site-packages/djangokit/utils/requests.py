#
# Copyright (c) 2018, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
"""
Вспомогательный функционал для обработки запросов.
"""
from django.contrib.auth import get_user_model


def get_ip_address(request, skip=None):
    meta = request.META
    ip = meta.get(
        'HTTP_X_REAL_IP', meta.get(
            'HTTP_X_FORWARDED_FOR', meta.get(
                'REMOTE_ADDR', ''
            )
        )
    )
    if ip and skip:
        if skip == 'local':
            skip = ('127.', '10.', '192.')
        for prefix in tuple(skip):
            if ip.startswith(prefix):
                return ''
    return ip


def get_cookies_domain2(request):
    """Возвращает домен второго уровня для кук."""
    host = request.get_host()
    domain = '.'.join(host.split('.')[-2:])
    if ':' in domain:
        domain = domain.split(':')[0]
    return domain


def get_user(request, user_id):
    user = request.user
    if user.id != user_id:
        user = get_user_model().objects.get(id=user_id)
    return user
