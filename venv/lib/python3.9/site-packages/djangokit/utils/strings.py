#
# Copyright (c) 2017, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from random import choice as random_choice
from uuid import uuid4

from django.utils.crypto import get_random_string
from django.utils.encoding import force_str
from django.utils.functional import Promise
from django.utils.translation import get_language, activate as on_language


def cut_text(obj, cut=255):
    """
    Преобразовывает объект в юникод и обрезает получившуюся строку.
    """
    s = force_str(obj)
    if len(s) > cut:
        return s[:cut]
    return s


def obfuscate_uuid():
    """
    Значение UUID обеспечивает абсолютную 30-летнюю уникальность в 128 бит,
    его обфускация - стойкость в 142 бита (log((6+6+10)**32, 2))
    """
    value = list(uuid4().hex)
    char_indexes = [i for i, char in enumerate(value) if char.isalpha()]
    length = len(char_indexes)
    # Если значение полностью состоит из цифр, то увы, обфускации не выйдет.
    if length > 1:
        random_list = [random_choice([1, 0]) for i in range(length)]
        for i, up in enumerate(random_list):
            if up:
                index = char_indexes[i]
                value[index] = value[index].upper()
    return ''.join(value)


def make_unique_secret(length=40):
    """
    Секретный ключ, с одной стороны, должен быть гарантированно уникальным,
    с другой - обеспечивать достаточную криптостойкость к брутфорсу, но
    при этом не содержать символов пунктуации, так как он может используется
    для авторизации из клиентских приложений.

    Значение UUID обеспечивает абсолютную 30-летнюю уникальность в 128 бит,
    его обфускация - стойкость в 142 бита (log((6+6+10)**32, 2)),
    а рандомный восьмисимвольный суффикс в 47 бит (log((26+26+10)**8, 2))
    - дополнительную гарантию от подбора сектретного ключа.
    """
    assert length >= 40
    return obfuscate_uuid() + get_random_string(length - 32)


def translate_text(lang, text, params=None):
    """
    Принимает текст в виде отложенного перевода и переводит его на язык
    пользователя.

    Все остальные параметры применяются к форматированию текста.

    Примеры использования:
    ----------------------

    >>> text = _('Team "Birds" vs team "Pigs"')
    >>> translate_text('ru', text)
    <<< Команда "Birds" против команды "Pigs"

    либо:

    >>> text = _('Team "%s" vs team "%s"')
    >>> params = [_('Birds'), _('Pigs')]
    >>> translate_text('ru', text, params)
    <<< Команда "Птицы" против команды "Свиньи"

    либо:

    >>> text = _('Team "%(team_1)s" vs team "%(team_2)s"')
    >>> params = {'team_1': _('Birds'), 'team2': _('Pigs')}
    >>> translate_text('ru', text, params)
    <<< Команда "Птицы" против команды "Свиньи"

    """

    def prepare(text, params):
        if isinstance(params, (list, tuple)):
            params = list(params)
            for i, a in enumerate(params):
                if isinstance(a, Promise):
                    params[i] = force_str(a)
            result = force_str(text % tuple(params))
        elif isinstance(params, dict):
            for k, v in params.items():
                if isinstance(v, Promise):
                    params[k] = force_str(v)
            result = force_str(text % params)
        elif params:
            raise ValueError('Params must be list, tuple or dictionary.')
        else:
            result = force_str(text)
        return result

    orig = get_language()
    if orig != lang:
        on_language(lang)
        result = prepare(text, params)
        on_language(orig)
    else:
        result = prepare(text, params)
    return result
