#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the same license as the current project.
#
import re
from django import template
from django.template.base import Node
from django.utils.functional import keep_lazy_text
from djangokit.utils.markdown import markdown_to_html

register = template.Library()


@keep_lazy_text
def strip_blanklines(value):
    return re.sub(r'\n\s*\n', '\n', str(value))


class BlanklineLessNode(Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        func = strip_blanklines
        return func(self.nodelist.render(context).strip())


@register.tag
def blanklineless(parser, token):
    """
    Remove blank lines.

    Example usage::

        {% blanklineless %}
        First Line

        Second line
        {% endblanklineless %}

    This example returns this text::

        First Line
        Second line

    """
    nodelist = parser.parse(('endblanklineless',))
    parser.delete_first_token()
    return BlanklineLessNode(nodelist)


@keep_lazy_text
def strip_spaces_html(value):
    return re.sub(r'\s+\\\n\s*', ' ', str(value))


@keep_lazy_text
def strip_spaces_javascript(value):
    value = re.sub(r'\s*\/\/.*\n\s*', '', str(value))
    return re.sub(r'\s*\n\s*', '', value)


class NewlineLessNode(Node):
    def __init__(self, nodelist, mode='html'):
        self.nodelist = nodelist
        self.mode = mode

    def render(self, context):
        if self.mode == 'javascript':
            func = strip_spaces_javascript
        else:
            func = strip_spaces_html
        return func(self.nodelist.render(context).strip())


@register.tag
def newlineless(parser, token):
    """
    Remove escaped newline and whitespace between chars, including tab and
    newline characters.

    Example usage::

        {% newlineless %}
            <a href="foo/" \
               class="bar"> \
                Foo \
            </a>
        {% endnewlineless %}

    This example returns this HTML::

        <a href="foo/" class="bar"> Foo </a>

    """
    nodelist = parser.parse(('endnewlineless',))
    parser.delete_first_token()
    return NewlineLessNode(nodelist)


@register.tag
def newlineless_javascript(parser, token):
    """
    Remove newline and whitespace between chars, including tab and
    newline characters.

    Example usage::

        {% newlineless_javascript %}
            var a = "foo/",
                b = "bar"
            ;
        {% endnewlineless_javascript %}

    This example returns this HTML::

        var a = "foo/",b = "bar";

    """
    nodelist = parser.parse(('endnewlineless_javascript',))
    parser.delete_first_token()
    return NewlineLessNode(nodelist, mode='javascript')


@register.filter
def markdown(text, code_style=None):
    return markdown_to_html(text, code_style)
