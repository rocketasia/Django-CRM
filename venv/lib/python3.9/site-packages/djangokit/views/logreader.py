#
# Copyright (c) 2020, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from os import listdir, stat
from os.path import basename, join, exists
from django.views.generic import View
from djangokit.utils.responses import JsonResponse


class LogReaderView(View):
    """
    AJAX-представление, считывающее построчно log-файлы из определённого
    каталога. Для ограничения доступа
    """
    logdir = None
    maxlines = 1000

    def _tail(self, filename: str, lines: int):
        """Считывает конец файла с некоторым количеством строк перед ним."""
        f = open(filename, 'rb')
        # Чтобы не проходить по очень большим логам, представим, что в среднем
        # строки длиной 1024 байта и перейдём на N килобайт до конца файла.
        avg_size = 1024 * lines
        if stat(filename).st_size > avg_size:
            f.seek(-avg_size, 2)
        buf = []
        i = 0
        for line in f:
            buf.append(line)
            i += 1
            if i // lines == 0:
                buf = buf[-lines:]
        buf = buf[-lines:]
        end = f.tell()
        f.close()
        return {
            'lines': [line.decode('utf-8').rstrip('\n') for line in buf],
            'end': end,
        }

    def _read(self, filename: str, lines: int, start: int):
        """Считывает строки файла начиная с позиции."""
        f = open(filename, 'rb')
        f.seek(start)
        buf = []
        i = 0
        for line in f:
            buf.append(line.decode('utf-8').rstrip('\n'))
            i += 1
            if i >= lines:
                break
        end = f.tell()
        f.close()
        return {
            'lines': buf,
            'end': end,
        }

    def _listdir(self, logdir: str):
        files = sorted([f for f in listdir(logdir) if f.endswith('.log')])
        return {'files': files}

    def render_to_response(self, context):
        return JsonResponse(context)

    def get(self, request, logfile=None, start=-1, lines=10):
        logdir = self.logdir
        context = {}
        if logfile:
            try:
                start = int(request.GET.get('start', start))
            except ValueError:
                pass
            try:
                lines = int(request.GET.get('lines', lines))
            except ValueError:
                pass
            filename = join(logdir, basename(logfile))
            if exists(filename):
                if lines > self.maxlines:
                    lines = self.maxlines
                if start >= 0:
                    context = self._read(filename, lines, start)
                else:
                    context = self._tail(filename, lines)
        elif logdir and exists(logdir):
            context = self._listdir(logdir)
        return self.render_to_response(context)
