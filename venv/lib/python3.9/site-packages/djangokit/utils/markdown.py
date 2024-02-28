#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
try:
    from markdown import markdown
    from pygments.styles import STYLE_MAP
except ImportError:
    use_markdown = False
    STYLE_MAP = {}
else:
    use_markdown = True

from django.utils.safestring import mark_safe

_html_escapes = {
    ord('&'): '&amp;',
    ord('<'): '&lt;',
    ord('>'): '&gt;',
    # ord('"'): '&quot;',
    # ord("'"): '&#39;',
}


def _markdown(source, code_style):
    if not use_markdown:
        return source
    if not code_style or code_style not in STYLE_MAP:
        code_style = 'default'
    conf = {
        'codehilite': {
            'linenums': False,
            'css_class': 'text-monospace codehilite',
            'noclasses': True,
            'pygments_style': code_style,
        }
    }
    extensions = [
        'attr_list',
        'fenced_code',
        'codehilite',
        'tables',
    ]
    return markdown(source, extensions=extensions, extension_configs=conf)


def markdown_to_html(source, code_style=None):
    """
    Обработка Markdown с подстветкой синтаксиса через Pygments для блоков кода
    в стиле GitHub-Flavored Markdown.
    """
    text = []
    code_started = False

    for s in source.split('\n'):
        start_gfm_code = s.strip().startswith('```')
        if start_gfm_code and not code_started:
            text.append(s)
            code_started = True
        elif start_gfm_code and code_started:
            text.append(s)
            code_started = False
        elif code_started:
            text.append(s)
        else:
            # Всё остальное нужно обработать от внедрения кода.
            text.append(mark_safe(str(s).translate(_html_escapes)))
    prepared = '\n'.join(text)
    return _markdown(prepared, code_style)
