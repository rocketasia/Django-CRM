#
# Copyright (c) 2018, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from os import remove
from os.path import exists

from PIL import Image
from PIL.ExifTags import TAGS


def get_or_create_thumbnail(path, thumb_path, force=False, size=(256, 256),
                            raise_exception=True):
    """
    Создаёт и возвращает объект уменьшенного изображения.
    """
    ex = exists(thumb_path)
    try:
        if force or not ex:
            # (Re)Create thumbnail
            if ex:
                remove(thumb_path)
            img = Image.open(path)
            try:
                exif = img._getexif()
            except Exception:
                exif = None
            if exif is not None:
                for tag, value in exif.items():
                    decoded = TAGS.get(tag, tag)
                    if decoded == 'Orientation':
                        if value == 3:
                            img = img.rotate(180)
                        elif value == 6:
                            img = img.rotate(270)
                        elif value == 8:
                            img = img.rotate(90)
                        break
            rgb = img.convert('RGB')
            rgb.thumbnail(size, Image.ANTIALIAS)
            rgb.save(thumb_path, 'JPEG')
    except IOError as e:
        if raise_exception:
            raise e
        return None
    return thumb_path
