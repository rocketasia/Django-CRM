#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

from djangokit.access.functions import user_access


def user_access_required(function=None, login_url=settings.LOGIN_URL,
                         raise_exception=False, checker=user_access):
    """
    Decorator for views that checks whether a user access.
    """
    def check_perms(user):
        # First, check if the user has permission.
        if checker(user):
            return True
        # If you need a 403 handler, throw an exception.
        if raise_exception:
            raise PermissionDenied
        # Or show the entry form.
        return False
    actual_decorator = user_passes_test(check_perms, login_url=login_url)
    if function:
        return actual_decorator(function)
    return actual_decorator
