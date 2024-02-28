#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
"""
Дополнения для django.apps
"""
from django.apps import apps


class DependencesMixin(object):
    """
    Mixin for automatic dependency checking in INSTALLED_APPS.

    Example::

        from django.apps import AppConfig
        from djangokit.utils.apps import DependencesMixin

        class UsersConfig(DependencesMixin, AppConfig):
            name = 'project.users'
            dependences = [
                'django.contrib.sites',
                'django.contrib.staticfiles',
                'django.contrib.sessions',
                'project.core',
            ]

    """
    dependences = None

    def check_dependences(self):
        if self.dependences:
            from django.conf import settings
            from django.core.exceptions import ImproperlyConfigured

            for d in self.dependences:
                if d not in settings.INSTALLED_APPS:
                    raise ImproperlyConfigured(
                        'Application "%s" depends from "%s". But not added '
                        'yet it into INSTALLED_APPS.' % (self.name, d)
                    )

    def ready(self):
        """
        Override this method in subclasses to run code when Django starts.
        """
        self.check_dependences()


def get_dependences_map(package=None):
    configs = apps.get_app_configs()
    L = [(c.name, getattr(c, 'dependences', [])) for c in configs]
    if package:
        packdot = package if package.startswith('.') else package + '.'
        return [x for x in L if x[0] == package or x[0].startswith(packdot)]
    return L
