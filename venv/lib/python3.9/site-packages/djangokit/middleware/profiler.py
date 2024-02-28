#
# Copyright (c) 2022, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#

from io import StringIO
from pstats import Stats
try:
    from cProfile import Profile
except ImportError:
    from profile import Profile

from django.conf import settings
from django.http import HttpResponse


def profile(get_response):
    """
    В режиме DEBUG возвращает результат работы профилировщика при указании в
    запросе параметра `__profile_view`, либо при наличии в запросе
    заголовка `Profile-View`.
    """

    def check_request(request):
        return '__profile_view' in request.GET or \
            'profile-view' in request.headers

    def middleware(request):
        if settings.DEBUG and check_request(request):
            profiler = Profile()
            profiler.runcall(get_response, request)
            profiler.create_stats()

            io = StringIO()
            stats = Stats(profiler, stream=io)
            stats.print_stats()

            return HttpResponse(io.getvalue(),
                                content_type='text/plain; charset=utf-8')

        return get_response(request)

    return middleware
