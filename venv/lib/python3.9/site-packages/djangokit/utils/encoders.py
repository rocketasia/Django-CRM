#
# Copyright (c) 2018, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from datetime import datetime, date, time
from decimal import Decimal
from json import JSONEncoder as OrigJSONEncoder, dumps, loads
from types import GeneratorType
from uuid import UUID

from django.utils.encoding import force_str
from django.utils.functional import Promise
from django.utils.timezone import is_aware


class JSONEncoder(OrigJSONEncoder):
    """
    Подкласс JSONEncoder, который умеет кодировать дату/время, числовой тип,
    генераторы, ленивые объекты перевода и исключения. Почти как в Django, но
    с дополнениями и чуть быстрее.
    """
    use_time_isoformat = True

    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime):
            r = o.isoformat()
            if not self.use_time_isoformat and o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, time):
            iso = self.use_time_isoformat
            if not iso and is_aware(o):
                raise ValueError("JSON can't represent timezone-aware times.")
            r = o.isoformat()
            if not iso and o.microsecond:
                r = r[:12]
            if iso and r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, Decimal):
            return float(o)
        elif isinstance(o, UUID):
            return str(o)
        elif isinstance(o, Exception):
            return force_str(o)
        elif isinstance(o, Promise):
            return force_str(o)
        elif isinstance(o, GeneratorType):
            return list(o)
        else:
            return super(JSONEncoder, self).default(o)


def dump_to_json(data, **kwargs):
    kwargs.setdefault('cls', JSONEncoder)
    return dumps(data, **kwargs)


def dump_from_json(string):
    return loads(string)
