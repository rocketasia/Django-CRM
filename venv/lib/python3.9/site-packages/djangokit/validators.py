#
# Copyright (c) 2018, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from django.core import validators
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class PhoneValidator(validators.RegexValidator):
    regex = r'^\+(9[976]\d|8[987530]\d|6[987]\d|5[90]\d|42\d|3[875]\d|2[98654321]\d|9[8543210]|8[6421]|6[6543210]|5[87654321]|4[987654310]|3[9643210]|2[70]|7|1)\d{1,14}$'
    message = _('Введите правильный телефонный номер.')


@deconstructible
class WebmoneyIDValidator(validators.RegexValidator):
    regex = r'^\d{12}$'
    message = _('Введите правильный идентификтор Webmoney.')


@deconstructible
class WebmoneyWalletValidator(validators.RegexValidator):
    regex = r'^[R,Z]\d{12}$'
    message = _('Укажите правильный Webmoney-кошелёк.')


@deconstructible
class YandexMoneyWalletValidator(validators.RegexValidator):
    regex = r'^\d{11,16}$'
    message = _('Укажите правильный кошелёк от Яндекс-Денег.')


@deconstructible
class SteamIDValidator(validators.RegexValidator):
    regex = r'^\d{17}$'
    message = _('Введите правильный идентификтор Steam.')


@deconstructible
class SteamTradeLinkValidator(validators.RegexValidator):
    regex = r'^https://steamcommunity.com/tradeoffer/new/\?partner=[0-9]+&token=[a-zA-Z0-9_-]+$'
    message = _('Введите правильную ссылку на обмен в Steam.')


@deconstructible
class UUIDValidator(validators.RegexValidator):
    regex = r'^[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}'
    message = _('Введите правильный UUID.')


@deconstructible
class BitcoinAddressValidator(validators.RegexValidator):
    regex = r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$'
    message = _('Введите правильный платёжный Bitcoin-адрес.')
