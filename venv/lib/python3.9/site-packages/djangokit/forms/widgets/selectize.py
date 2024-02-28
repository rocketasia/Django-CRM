#
# Copyright (c) 2019, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from django import forms
from django.http import QueryDict
from django.shortcuts import resolve_url


class SelectizeMixin(object):
    # refurl_template_name = ''

    def __init__(self, refurl=None, filters=None, create=False, *args, **kwargs):
        self.refurl = refurl
        self.filters = filters
        self.has_create_object = create
        if refurl:
            self.template_name = self.refurl_template_name
        super().__init__(*args, **kwargs)

    def get_context(self, name, value, attrs):
        classes = [c for c in attrs.get('class', '').split(' ') if c]
        if 'selectize-is-not-set' not in classes:
            classes.append('selectize-is-not-set')
        attrs['class'] = ' '.join(classes)
        if self.has_create_object:
            attrs['data-create'] = 'true'
        # Собираем контент для нашего шаблона.
        if self.refurl:
            return self.get_refurl_context(name, value, attrs)
        # Отдаём контент для встроенного шаблона.
        return super().get_context(name, value, attrs)

    def get_refurl_context(self, name, value, attrs):
        attrs['data-url'] = resolve_url(self.refurl)
        if self.filters:
            query = QueryDict('', mutable=True)
            for k, v in self.filters.items():
                if isinstance(v, (tuple, list)):
                    v = ','.join(v)
                query.appendlist(k, v)
            query._mutable = False
            attrs['data-filters'] = query.urlencode()
        if isinstance(value, (tuple, list)):
            value = [x for x in value if x]
        context = {}
        context['widget'] = {
            'name': name,
            'is_hidden': self.is_hidden,
            'required': self.is_required,
            'value': self.format_value(value),
            'attrs': self.build_attrs(self.attrs, attrs),
            'template_name': self.template_name,
        }
        if self.allow_multiple_selected:
            context['widget']['attrs']['multiple'] = True
        if value:
            context['value'] = self.get_instance(value)
        return context

    def get_instance(self, value):
        qs = self.choices.queryset
        if isinstance(value, (tuple, list)):
            return qs.filter(pk__in=value)
        return qs.get(pk=value)


class Selectize(SelectizeMixin, forms.Select):
    refurl_template_name = 'djangokit/widgets/selectize.html'


class SelectizeMultiple(SelectizeMixin, forms.SelectMultiple):
    refurl_template_name = 'djangokit/widgets/selectize_multiple.html'
