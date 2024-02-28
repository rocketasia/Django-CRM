#
# Copyright (c) 2018, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
import traceback
from functools import wraps
from logging import getLogger

from django.utils.encoding import force_str
from django.utils.log import AdminEmailHandler as BaseAdminEmailHandler


class AdminErrorHandler(BaseAdminEmailHandler):
    """Обработчик логгера запускаемых команд, отправляющий почту админам."""

    def emit(self, record):
        subject = message = None

        if hasattr(record, 'command') and hasattr(record, 'exception'):
            command = record.command
            name = command.__class__.__module__.split('.')[-1]
            subject = 'Something went wrong in %s' % name

            exception = record.exception
            message = ''.join(traceback.format_exception(
                etype=type(exception),
                value=exception,
                tb=exception.__traceback__,
            ))
            if hasattr(record, 'command_args'):
                message += '\n\nARGS:\n    %s' % '\n    '.join(
                    [force_str(i) for i in record.command_args]
                )
            if hasattr(record, 'command_kwargs'):
                message += '\n\nKWARGS:\n    %s' % '\n    '.join(
                    ['%s=%s' % (force_str(k), force_str(v)) for k, v in
                     record.command_kwargs.items()]
                )
        else:
            subject = '%s: %s' % (
                record.levelname,
                record.getMessage()
            )
            subject = self.format_subject(subject)
            message = 'Undefined message, please check server logs.'

        self.send_mail(subject, message, fail_silently=True)


def handler_logging(method=None, level='error', logger_or_name='management'):
    """
    Декоратор для метода handler команды, который отправляет логгеру
    ошибки исполнения.
    """

    # Проверяем наличие метода в момент определения кода.
    assert level in ('debug', 'info', 'warning', 'error', 'critical')
    if isinstance(logger_or_name, str):
        logger = getLogger(logger_or_name)
    else:
        logger = logger_or_name
    log_func = getattr(logger, level)

    def decorator(method_func):
        @wraps(method_func)
        def _wrapped_method(self, *args, **kwargs):
            try:
                return method_func(self, *args, **kwargs)
            except Exception as e:
                log_func(
                    force_str(e),
                    extra={
                        'command': self,
                        'command_args': args,
                        'command_kwargs': kwargs,
                        'exception': e,
                    }
                )
                raise e
        return _wrapped_method

    if method:
        return decorator(method)
    return decorator
