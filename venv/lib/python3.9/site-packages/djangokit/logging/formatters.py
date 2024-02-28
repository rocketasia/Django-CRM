#
# Copyright (c) 2020, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
import logging
from django.core.management.color import color_style


class ColorFormatter(logging.Formatter):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.style = color_style(force_color=True)
        self.setup_colorizers()

    def setup_colorizers(self):
        """Установка методов цветового оформления."""
        style = self.style
        self.colorizers = {
            'NOTSET': style.HTTP_SUCCESS,  # без цвета
            'DEBUG': style.HTTP_NOT_MODIFIED,
            'INFO': style.SUCCESS,
            'WARNING': style.WARNING,
            'ERROR': style.ERROR,
            'CRITICAL': style.HTTP_SERVER_ERROR,
        }
        self.default_colorizer = style.HTTP_SUCCESS

    def format(self, record):
        message = super().format(record)
        colorize = self.colorizers.get(record.levelname, self.default_colorizer)
        return colorize(message)
