#
# Copyright (c) 2018, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from django.conf import settings
from django.shortcuts import render, redirect


class MaintenanceMiddleware:
    """
    Middleware постановки сайта на обслуживание.

    Если в настройках включена настройка MAINTENANCE,
    на все запросы отдает страницу maintenance.html c кодом 404, чтобы
    сообщить, что этот документ в ближайшее время будет восстановлен.

    Шаблон и код ответа можно переопределить через наследование класса.
    """

    template_name = 'maintenance.html'
    status_code = 404
    on = False

    def __init__(self, get_response):
        self.get_response = get_response
        self.on = getattr(settings, 'MAINTENANCE', False)

    def __call__(self, request):
        if not self.on:
            return self.get_response(request)
        return render(request, self.template_name, status=self.status_code)


class SeparateAccessMiddleware:
    """
    Middleware для выборочного доступа ко всем ресурсам сайтов.

    Если в настройках включена настройка USE_SEPARATE_ACCESS,
    то каждый запрос проверяется на выборочный доступ, и если он не
    проходит, то на все запросы отдает страницу separate_access.html и код 403.
    На данной странице предлагается ввести ключ, который отредиректит
    строго на главную страницу.

    Внимание! Не добавляйте эту прослойку в административный сайт, если
    используете параметр, получаемый из своей модели параметров в базе данных
    через кастомизированный метод `get_key_from_db`. Да, этот метод нужен
    именно для переопределения в своих проектах.
    """
    template_name = 'separate_access.html'
    status_code = 403
    separate_access_key = ''
    session_key_name = 'access_key'
    post_key_name = 'access_key'

    def __init__(self, get_response):
        self.get_response = get_response
        self.separate_access_key = getattr(settings, 'SEPARATE_ACCESS_KEY', '')

    def __call__(self, request):
        # Без ключей это должно работать быстро. Поэтому сначала
        # просто проверяем наличие ограничения.
        separate_access_key = self.separate_access_key
        if not separate_access_key:
            return self.get_response(request)
        _key = self.get_key_from_db(request, separate_access_key)
        # Затем проверяем ключ из сессии на актуальность.
        session_key_name = self.session_key_name
        session = request.session
        access_key = session.get(session_key_name)
        if access_key == _key:
            return self.get_response(request)
        elif access_key:
            del session[session_key_name]
        # Проверка ключа доступа в параметрах запроса.
        if request.method == 'POST':
            access_key = request.POST.get(self.post_key_name)
            if access_key == _key:
                session[session_key_name] = access_key
                return redirect(request.path)
        return render(request, self.template_name, status=self.status_code)

    def get_key_from_db(self, request, default):
        return default
