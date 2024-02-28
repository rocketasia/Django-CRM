#
# Copyright (c) 2018, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
import os
from unidecode import unidecode


def remove_file(filename):
    """Замалчивание ошибки удаления файла."""
    try:
        os.remove(filename)
        return True
    except OSError:
        return False


def remove_dirs(dirname, withfiles=False):
    """Замалчивание ошибки удаления каталога."""
    if withfiles and os.path.exists(dirname):
        for f in os.listdir(dirname):
            remove_file(os.path.join(dirname, f))
    try:
        os.removedirs(dirname)
        return True
    except OSError:
        return False


def secure_filename(s):
    """
    Преобразовывает имена разных алфавитов в латинницу и удаляет/заменяет
    лишние символы.
    """
    return unidecode(s).replace(' ', '_').replace("'", "")
