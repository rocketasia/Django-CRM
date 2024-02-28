#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
"""
Functions for access control.
"""
from django.conf import settings

USER_ACCESS_LEVEL = getattr(settings, 'USER_ACCESS_LEVEL', 'user')


def check_user(user):
    """For authenticated users."""
    return user.is_active and user.is_authenticated


def check_employer(user):
    """For employers and superusers."""
    return check_user(user) and (user.is_staff or user.is_superuser)


def check_superuser(user):
    """For superusers."""
    return check_user(user) and user.is_superuser


levels = {
    'anonymous': lambda u: True,
    'user': check_user,
    'employer': check_employer,
    'superuser': check_superuser,
}
# Автоматически выбранная по настройке settings.USER_ACCESS_LEVEL функция.
user_access = levels[USER_ACCESS_LEVEL]
