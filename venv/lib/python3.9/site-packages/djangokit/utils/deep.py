#
# Copyright (c) 2016, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
"""Модуль, помогающий обрабатывать глубоко вложенные структуры.
"""
from types import GeneratorType


def split_field(field):
    """Разбивка на поля."""
    if not isinstance(field, (list, tuple)):
        return field.split('.')
    fields = []
    for f in field:
        if not isinstance(f, (list, tuple)):
            f = f.split('.')
        fields.extend(f)
    return fields


def to_dict(dic, field, value, append_to_list=False):
    """
    Рекурсивное обновление поля словаря.

    Ключ значения может выглядеть как:
    'field'
    или
    'field1.field2.field3'
    или
    ['field1', 'field2', 'field3.field4', ...]

    Заметьте, что (по умолчанию) списки поддерживаются только в
    качестве готовых значений! Если нужно добавить в список, то
    передавайте параметр `append_to_list=True`.
    Тогда, если такого списка нет, то он создастся с переданным
    значением внутри, если же есть и это действительно список,
    то добавит в него. Если же назначение не список, то вызовет ошибку.
    """
    D = dic

    if not isinstance(D, dict):
        D = {}

    field = split_field(field)

    d = D
    length = len(field)
    dest = length - 1
    for i in range(0, length):
        key = field[i]
        if key not in d:
            if i == dest:
                if append_to_list:
                    d[key] = [value]
                else:
                    d[key] = value
            else:
                d[key] = {}
                d = d[key]
        elif i == dest:
            if append_to_list:
                d[key].append(value)
            else:
                d[key] = value
        else:
            d = d[key]

    return D


def from_dict(dic, field, default=None, update=False, delete=False):
    """
    Рекурсивное получение поля словаря.

    Ключ значения может выглядеть как:
    'field'
    или
    'field1.field2.field3'
    или
    ['field1', 'field2', 'field3.field4', ...]

    Если задано обновление, то в случае отсутствия значения изменит
    словарь, установив значение по-умолчанию.

    Если задано удаление, то удаляет этот ключ.

    """
    D = dic

    if not isinstance(D, dict):
        D = {}

    field = split_field(field)

    d = D
    value = default
    length = len(field)
    dest = length - 1
    for i in range(0, length):
        key = field[i]
        if key not in d:
            if not update or delete:
                break
            elif i == dest:
                d[key] = value
            else:
                d[key] = {}
                d = d[key]
        elif i == dest:
            if delete:
                value = d.pop(key)
                break
            else:
                value = d[key]
        else:
            d = d[key]

    if callable(value):
        return value()
    else:
        return value


def to_flat_list(data, skip=None, prebool=None, sort=False):
    """
    Преобразовывает многоуровневый объект в [отсортированный] плоский список.
    """
    result = []
    if skip is None:
        skip = ()
    if prebool is None:
        prebool = int

    def collect(item, prefix=''):
        if isinstance(item, dict):
            for key, value in item.items():
                if key in skip:
                    continue
                # Recursive collection for internal values.
                collect(value, prefix='%s%s:' % (prefix, key))
        elif isinstance(item, (list, tuple, range, GeneratorType)):
            for key, value in enumerate(item):
                # Recursive collection for internal values.
                collect(value, prefix='%s%d:' % (prefix, key))
        else:
            if isinstance(item, bool):
                value = prebool(item)
            else:
                value = item
            result.append('%s%s' % (prefix, str(value)))

    collect(data)
    if sort:
        result.sort()
    return result


def to_unique_string(data, skip=None, prebool=None, separator=';'):
    """
    Преобразовывает многоуровневый объект в уникальную строку.
    """
    if data is None:
        return ''
    elif isinstance(data, str):
        return data
    flat_list = to_flat_list(data, skip=skip, prebool=prebool, sort=True)
    return separator.join(flat_list)
