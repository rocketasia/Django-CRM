#
# Copyright (c) 2018, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
"""
Функционал для сериализации данных из моделей.
"""
import logging

from django.db.models import Model, Manager
from django.db.models.fields.files import FieldFile
from django.utils.encoding import force_str

logger = logging.getLogger(__name__)


def _simple_serializer(instance):
    return [
        instance.pk,
        force_str(instance),
    ]


def _complex_serializer(instance):
    return {
        'pk': instance.pk,
        'display_name': force_str(instance),
        # Затем словарь можно дополнить в коде следующим образом:
        # 'fields': {},
        # 'url': reverse(...),
    }


class ObjectSerializer:
    """
    Cериализация полей объекта модели.

    Если передан список полей "only" - то сериализует только их, если его нет,
    то сериализует все поля, за исключением списка "exclude".

    По умолчанию передаётся флаг "simple" и данные формируются в упрощённом
    виде.

    Пример "упрощённой" сериализации:
    ---------------------------------

    post_serializer = ObjectSerializer(exclude=['details'])

    data = post_serializer(post)
    data['url'] = resolve_url(
        'blogs:post', post_furl=post.furl, blog_furl=post.blog.furl,
    )
    # Дополнение поля blog:
    data['blog'][2] = post.blog.furl
    # Дополнение вычисляемых свойств:
    data['count_views'] = post.get_count_views()

    Результатом будет:
    {
        'id': 2,
        'created': '2018-01-01T20:00:00Z',
        'name': 'First post',
        'blog': [1, 'First blog (author: User)', 'first-blog'],
        'count_views': 10,
        'url': '/blogs/first-blog/first-post/',
    }

    Пример "сложной" сериализации:
    ------------------------------

    post_serializer = ObjectSerializer(
        exclude=['blog', 'details'], simple=False
    )
    blog_serializer = ObjectSerializer(only=['name', 'furl'])

    data = post_serializer(post)
    data['url'] = resolve_url(
        'blogs:post', post_furl=post.furl, blog_furl=post.blog.furl,
    )
    # Дополнение поля blog:
    data['fields']['blog'] = blog_serializer(post.blog)
    # Дополнение вычисляемых свойств:
    data['count_views'] = post.get_count_views()

    Результатом будет:
    {
        'display_name': 'First post at 20:00',
        'fields': {
            'id': 2,
            'created': '2018-01-01T20:00:00Z',
            'name': 'First post',
            'blog': {
                'fields': {
                    'furl': 'first-blog',
                    'name': 'First blog',
                }
                'pk': 1,
                'display_name': 'First blog (author: User)',
            }
        },
        'count_views': 10,
        'pk': 2,
        'url': '/blogs/first-blog/first-post/',
    }

    """
    model = None
    only = ()
    exclude = ()
    simple = True

    def __init__(self, model=None, only=None, exclude=None, simple=None):
        if model is not None:
            self.model = model
        if only is not None:
            self.only = only
        elif exclude is not None:
            self.exclude = exclude
        if simple is not None:
            self.simple = simple
        self.is_ready = False
        if self.model:
            self.set_fields(self.model._meta)

    def __call__(self, instance, *args, **kwargs):
        # logger.debug('%s: %s args=%s kwargs=%s', self, instance, args, kwargs)
        return self.serialize(instance, *args, **kwargs)

    def set_fields(self, meta):
        # Собираем все поля в одну кучу.
        all = [f for f in meta.fields]
        if meta.many_to_many:
            all.extend([f for f in meta.many_to_many])
        # Составляем список необходимых полей.
        if self.only:
            list_fields = [f for f in all if f.name in self.only]
        elif self.exclude:
            list_fields = [f for f in all if f.name not in self.exclude]
        else:
            list_fields = all
        self.list_fields = list_fields
        self.is_ready = True
        return list_fields

    def serialize(self, instance, *args, **kwargs):
        """Полная сериализация экземпляра."""
        if not self.is_ready:
            self.set_fields(instance._meta)

        simple = self.simple
        if simple:
            serializer = _simple_serializer
            result = {}
            fields = result
        else:
            serializer = _complex_serializer
            result = serializer(instance)
            fields = result['fields'] = {}

        for f in self.list_fields:
            name = f.name
            value = None
            data = getattr(instance, name, None)
            if isinstance(data, FieldFile):
                if data.name:
                    value = data.url
            elif isinstance(data, Model):
                value = serializer(data)
            elif isinstance(data, Manager):
                value = [serializer(i) for i in data.all()]
            else:
                value = data
            fields[name] = value
        return self.extend(instance=instance, data=result, *args, **kwargs)

    def extend(self, instance, data, *args, **kwargs):
        """Метод для расширения стандартной сериализации."""
        return data
