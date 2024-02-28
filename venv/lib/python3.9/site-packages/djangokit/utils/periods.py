#
# Copyright (c) 2016, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from datetime import timedelta
from djangokit.utils.datetimes import datetime_local as now


def gethours(dst=(0, 0), from_datetime=None, **kwargs):
    """
    Возвращает точки начала и конца часа.
    Параметром dst (кортеж из двух целых чисел) задаётся количество
    часов от текущего для начала и конца периода.
    Наример, если dst == (0, 1) то вернёт:
    (начало-текущего-часа, конец-следующего)
    """
    dt = from_datetime if from_datetime else now()
    start = dt.replace(minute=0, second=0, microsecond=0)
    end = start.replace(minute=59, second=59, microsecond=999999)
    return (start + timedelta(hours=dst[0]), end + timedelta(hours=dst[1]))


def hour(**kwargs):
    return gethours(dst=(0, 0), **kwargs)


def next_hour(**kwargs):
    return gethours(dst=(1, 1), **kwargs)


def previous_hour(**kwargs):
    return gethours(dst=(-1, -1), **kwargs)


def getdays(dst=(0, 0), withtime=True, from_datetime=None, **kwargs):
    """
    Возвращает точки начала и конца дня.
    Параметром dst (кортеж из двух целых чисел) задаётся количество
    дней от текущего для начала и конца периода.
    Наример, если dst == (0, 1) то вернёт:
    (начало-текущего-дня, конец-завтрашнего)
    """
    dt = from_datetime if from_datetime else now()
    if withtime:
        start = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start.replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        start = end = dt.date()
    return (start + timedelta(days=dst[0]), end + timedelta(days=dst[1]))


def today(**kwargs):
    return getdays(dst=(0, 0), **kwargs)


def tomorrow(**kwargs):
    return getdays(dst=(1, 1), **kwargs)


def tomorrow2(**kwargs):
    return getdays(dst=(2, 2), **kwargs)


def yesterday(**kwargs):
    return getdays(dst=(-1, -1), **kwargs)


def yesterday2(**kwargs):
    return getdays(dst=(-2, -2), **kwargs)


def next2days(**kwargs):
    return getdays(dst=(1, 2), **kwargs)


def next3days(**kwargs):
    return getdays(dst=(1, 3), **kwargs)


def last2days(**kwargs):
    return getdays(dst=(-2, -1), **kwargs)


def last3days(**kwargs):
    return getdays(dst=(-3, -1), **kwargs)


def week(dst=0, firstweekday=1, withtime=True, from_datetime=None, **kwargs):
    """
    Возвращает точки начала и конца недели.
    Параметром dst (целое число) задаётся количество недель от текущей.
    Наример, если dst == 1 то вернёт:
    (начало-следующей-недели, конец-следующей-недели)
    """
    n = from_datetime if from_datetime else now()
    if withtime:
        n = n.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        n = n.date()

    start = n - timedelta(days=n.weekday() - firstweekday + 1)
    if dst:
        start = start + timedelta(days=(dst * 7))
    if withtime:
        end = start + timedelta(days=7) - timedelta(microseconds=1)
    else:
        end = start + timedelta(days=6)

    return (start, end)


def next_week(**kwargs):
    return week(dst=1, **kwargs)


def previous_week(**kwargs):
    return week(dst=-1, **kwargs)


def get_next_month(dt):
    n_month = ((dt.month + 1) % 12) or 12
    n_year = dt.year + (dt.month // 12)
    return dt.replace(year=n_year, month=n_month, day=1)


def month(dst=0, withtime=True, from_datetime=None, **kwargs):
    """
    Возвращает точки начала и конца месяца.
    Параметром dst (целое число) задаётся количество месяцев от текущего.
    Наример, если dst == 1 то вернёт:
    (начало-следующго-месяца, конец-следующего-месяца)
    """
    n = from_datetime if from_datetime else now()
    if withtime:
        n = n.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        n = n.date().replace(day=1)

    month = n.month
    year = n.year

    if dst < 0:
        month = ((n.month - ((abs(dst)) % 12)) % 12) or 12
        year = n.year - ((abs(dst) + 12 - n.month) // 12)
    elif dst > 0:
        month = ((n.month + ((abs(dst)) % 12)) % 12) or 12
        year = n.year + ((abs(dst) + n.month - 1) // 12)

    start = n.replace(year=year, month=month)

    next_month = get_next_month(start)

    if withtime:
        end = next_month - timedelta(microseconds=1)
    else:
        end = next_month - timedelta(days=1)

    return (start, end)


def next_month(**kwargs):
    return month(dst=1, **kwargs)


def previous_month(**kwargs):
    return month(dst=-1, **kwargs)


def quarter1(withtime=True, from_datetime=None, **kwargs):
    n = from_datetime if from_datetime else now()
    if withtime:
        start = n.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = n.replace(
            month=3, day=31, hour=23, minute=59, second=59, microsecond=999999)
    else:
        n = n.date()
        start = n.replace(month=1, day=1)
        end = n.replace(month=3, day=31)
    return (start, end)


def quarter2(withtime=True, from_datetime=None, **kwargs):
    n = from_datetime if from_datetime else now()
    if withtime:
        start = n.replace(
            month=4, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = n.replace(
            month=6, day=30, hour=23, minute=59, second=59, microsecond=999999)
    else:
        n = n.date()
        start = n.replace(month=4, day=1)
        end = n.replace(month=6, day=30)
    return (start, end)


def quarter3(withtime=True, from_datetime=None, **kwargs):
    n = from_datetime if from_datetime else now()
    if withtime:
        start = n.replace(
            month=7, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = n.replace(
            month=9, day=30, hour=23, minute=59, second=59, microsecond=999999)
    else:
        n = n.date()
        start = n.replace(month=7, day=1)
        end = n.replace(month=9, day=30)
    return (start, end)


def quarter4(withtime=True, from_datetime=None, **kwargs):
    n = from_datetime if from_datetime else now()
    if withtime:
        start = n.replace(
            month=10, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = n.replace(
            month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    else:
        n = n.date()
        start = n.replace(month=10, day=1)
        end = n.replace(month=12, day=31)
    return (start, end)


def halfyear1(withtime=True, from_datetime=None, **kwargs):
    n = from_datetime if from_datetime else now()
    if withtime:
        start = n.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = n.replace(
            month=6, day=30, hour=23, minute=59, second=59, microsecond=999999)
    else:
        n = n.date()
        start = n.replace(month=1, day=1)
        end = n.replace(month=6, day=30)
    return (start, end)


def halfyear2(withtime=True, from_datetime=None, **kwargs):
    n = from_datetime if from_datetime else now()
    if withtime:
        start = n.replace(
            month=7, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = n.replace(
            month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    else:
        n = n.date()
        start = n.replace(month=7, day=1)
        end = n.replace(month=12, day=31)
    return (start, end)


def year(withtime=True, from_datetime=None, **kwargs):
    n = from_datetime if from_datetime else now()
    if withtime:
        start = n.replace(
            month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        end = n.replace(
            month=12, day=31, hour=23, minute=59, second=59, microsecond=999999)
    else:
        n = n.date()
        start = n.replace(month=1, day=1)
        end = n.replace(month=12, day=31)
    return (start, end)


def next_year(**kwargs):
    return [x.replace(year=x.year + 1) for x in year(**kwargs)]


def previous_year(**kwargs):
    return [x.replace(year=x.year - 1) for x in year(**kwargs)]
