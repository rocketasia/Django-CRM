#
# Copyright (c) 2018, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
"""Crypto functional utilites.
"""
from binascii import b2a_hex, a2b_hex
from Crypto.Random import new as random_new
from Crypto.Cipher.AES import new as cipher_new, block_size, MODE_CBC
from django.utils.encoding import force_bytes, force_str


class AESCipher(object):
    """
    Шифратор по алгоритму AES-128, AES-192 или AES-256 (в зависимости от
    размера "size") с кодированием результата в hex.

    Длина строки данных должна быть кратна 16. Для этого в качестве
    дополнителя используются нечитаемые символы с числом от 1 до 16.
    Например, пустая строка будет заполнена 16-ю '\x10', строка '1234567890'
    превратится в '1234567890\x06\x06\x06\x06\x06\x06'.

    По похожему принципу делаются пароли, но их длина может быть
    16, 24 или 32 символа.

    Заметьте, что для совместимости с Node.js используется MODE_CBC,
    так как другие варианты не обеспечивали расшифровку, хотя может быть
    это была временная ошибка, но так теперь прижилось.

    """

    def __init__(self, password='', size=16):
        assert size in (16, 24, 32), 'Not valid size "%s".' % size
        self.size = size
        self.name = {
            16: 'AES-128-CBC',
            24: 'AES-192-CBC',
            32: 'AES-256-CBC',
        }[size]
        passwd = force_bytes(password)
        length = len(passwd)
        if length > size:
            passwd = passwd[:size]
        elif length < size:
            need = size - (length % size)
            passwd += force_bytes(chr(0) * need)
        self.password = passwd

    def __str__(self):
        return self.name

    def encrypt(self, message):
        """Шифрование данных."""
        IV = random_new().read(block_size)
        aes = cipher_new(self.password, MODE_CBC, IV)
        message = force_bytes(message)
        mod = len(message) % 16
        message += force_bytes((16 - mod) * chr(16 - mod))
        encrypted = b2a_hex(IV) + b2a_hex(aes.encrypt(message))
        return force_str(encrypted)

    def decrypt(self, encrypted):
        """Дешифровка данных."""
        encrypted = a2b_hex(encrypted)
        IV = encrypted[:block_size]
        aes = cipher_new(self.password, MODE_CBC, IV)
        message = aes.decrypt(encrypted[block_size:])
        if message:
            # Python 3 автоматически возвращает число.
            number = message[-1]
            if not isinstance(number, int):
                number = ord(number)
            if number <= 16:
                message = message[:-number]
        else:
            message = ''
        return force_str(message)
