#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the same license as the current project.
#
from django import template
from django.urls import reverse
from django.utils.crypto import get_random_string

register = template.Library()


@register.simple_tag
def active(request, *urls, **kwargs):
    for url in urls:
        # Any a roots does not gets under activity.
        # Namespaces like 'blabla:index' (1 level) does not gets too.
        # But compound, like 'blabla:trololo:index' (2 level and more) gets
        # under activity.
        if (url != '/' and not url.endswith(':index')) or url.count(':') > 1:
            if request.path.startswith(reverse(url, kwargs=kwargs)):
                return "active"
    return ""


@register.simple_tag
def active_equal(request, url, **kwargs):
    if request.path == reverse(url, kwargs=kwargs):
        return "active"
    return ""


@register.simple_tag
def addparams(request, **kwargs):
    q = request.GET.copy()
    for k, v in kwargs.items():
        v = str(v)
        if v:
            q[k] = v
        else:
            q.pop(k, None)
    if q:
        return '?%s' % q.urlencode()
    return ''


@register.simple_tag
def toggleparams(request, **kwargs):
    q = request.GET.copy()
    for k, v in kwargs.items():
        if k in q:
            del q[k]
        else:
            q[k] = str(v)
    if q:
        return '?%s' % q.urlencode()
    return ''


@register.simple_tag
def delparams(request, *params):
    q = request.GET.copy()
    for name in params:
        q.pop(name, None)
    if q:
        return '?%s' % q.urlencode()
    return ''


def page_range_dots(page, on_each_side=3, on_ends=2, dot='.'):
    number = page.number
    paginator = page.paginator
    num_pages = paginator.num_pages
    if num_pages > 9:
        if number > (on_each_side + on_ends):
            page_range = [
                *range(1, on_each_side),
                dot,
                *range(number + 1 - on_each_side, number + 1),
            ]
        else:
            page_range = list(range(1, number + 1))

        if number < (num_pages - on_each_side - on_ends + 1):
            page_range.extend([
                *range(number + 1, number + on_each_side),
                dot,
                *range(num_pages - on_ends + 1, num_pages + 1),
            ])
        else:
            page_range.extend(range(number + 1, num_pages + 1))
    else:
        page_range = paginator.page_range
    return page_range


@register.filter
def make_page_range(page):
    return page_range_dots(page)


@register.filter
def split(s, sep=','):
    return s.split(sep)


@register.filter
def guid(s, length=12):
    return '%s-%s' % (s, get_random_string(length))
