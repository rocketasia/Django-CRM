#
# Copyright (c) 2018, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from functools import wraps
from os import remove
from os.path import exists

from django.utils.dateparse import parse_datetime
from django.utils.timezone import now, timedelta


class LockError(Exception):
    pass


def lockfile(method=None, filename=None, timeout=60 * 60):
    """
    Декоратор для метода handler команды вызов которой блокируется файлом.
    По умолчанию: название файла берётся по имени команды, блокировка на 1 час.
    """

    def get_filename(command):
        if not filename:
            return '%s.lock' % command.__class__.__module__.split('.')[-1]
        return filename

    def get_timeout():
        return timeout

    def decorator(method_func):
        @wraps(method_func)
        def _wrapped_method(self, *args, **kwargs):
            filename = get_filename(self)
            timeout = get_timeout()
            # TODO: UNIX only, please fix it.
            path = '/tmp/%s' % filename
            newtime = now()
            if exists(path):
                with open(path, 'r') as f:
                    line = f.readline()
                    time = parse_datetime(line)
                    if time and time + timedelta(seconds=timeout) > newtime:
                        raise LockError(
                            'Blocked by "%s" file at "%s"' % (path, time)
                        )
            f = open(path, 'w')
            f.write(newtime.isoformat())
            f.close()
            try:
                return method_func(self, *args, **kwargs)
            except Exception as e:
                raise e
            finally:
                remove(path)
        return _wrapped_method

    if method:
        return decorator(method)
    return decorator
