"""
Обработка QuerySet.
"""
from copy import deepcopy

import sqlparse
from django.db.models import Q
from django.shortcuts import _get_queryset


class CurrentUser:
    """
    Класс для подстановки в ленивые запросы текущего пользователя.
    """

    def __str__(self):
        return 'CURRENT_USER'

    def __eq__(self, obj):
        return isinstance(obj, self.__class__)


CURRENT_USER = CurrentUser()
# Удаляем класс, за ненадобностью.
del CurrentUser


class LazyFilters:
    """
    An object containing a set of filters whose value can be CURRENT_USER,
    which will be replaced with the request user ID (or None for anonymous
    users).

    Example:

    lazy_filters = LazyFilters(
        Q(id=CURRENT_USER),
        group__name='Membership',
    )
    lazy_filters = lazy_filters.filter(
        Q(date_joined=date(2005, 5, 2)) | Q(date_joined=date(2005, 5, 6)),
    )
    lazy_filters = lazy_filters.exclude(
        Q(is_staff=True) | Q(is_superuser=True),
        is_active=False,
    )

    is_winner = lazy_filters.apply(request, User.objects.all())
    """

    def __init__(self, *args, **kwargs):
        self._filter_args = ()
        self._filter_kwargs = {}
        self._exclude_args = ()
        self._exclude_kwargs = {}
        self.filter(*args, **kwargs)

    def __str__(self):
        include = [str(x) for x in self._filter_args]
        for k, v in self._filter_kwargs.items():
            include.append(f'{k}={v}')

        exclude = [str(x) for x in self._exclude_args]
        for k, v in self._exclude_kwargs.items():
            exclude.append(f'{k}={v}')

        parts = []
        if include:
            parts.append(f'(AND: {", ".join(include)})')
        if exclude:
            parts.append(f'~(AND: {", ".join(exclude)})')

        return ' & '.join(parts)

    def filter(self, *args, **kwargs):
        self._filter_args += args
        self._filter_kwargs = {
            **self._filter_kwargs,
            **kwargs
        }
        return self

    def exclude(self, *args, **kwargs):
        self._exclude_args += args
        self._exclude_kwargs = {
            **self._exclude_kwargs,
            **kwargs
        }
        return self

    def copy(self):
        new = self.__class__(*self._filter_args, **self._filter_kwargs)
        new.exclude(*self._exclude_args, **self._exclude_kwargs)
        return new

    def apply(self, request, queryset):
        # Filter.
        filter_args = self._filter_args
        if filter_args:
            filter_args = self.prepare_args(filter_args, request)
            queryset = queryset.filter(*filter_args)

        filter_kwargs = self._filter_kwargs
        if filter_kwargs:
            filter_kwargs = self.prepare_kwargs(filter_kwargs, request)
            queryset = queryset.filter(**filter_kwargs)

        # Exclude.
        exclude_args = self._exclude_args
        if exclude_args:
            exclude_args = self.prepare_args(exclude_args, request)
            queryset = queryset.exclude(*exclude_args)

        exclude_kwargs = self._exclude_kwargs
        if exclude_kwargs:
            exclude_kwargs = self.prepare_kwargs(exclude_kwargs, request)
            queryset = queryset.exclude(**exclude_kwargs)

        return queryset

    def prepare_args(self, args, request):
        user = getattr(request, 'user', None)
        user_id = user.id if user else None

        def q_from_request(q):
            children = q.children
            for i, child in enumerate(children):
                if isinstance(child, Q):
                    children[i] = q_from_request(child)
                elif isinstance(child, tuple) and len(child) == 2 and \
                        child[1] == CURRENT_USER:
                    children[i] = (child[0], user_id)
            return q

        new_args = []
        for arg in args:
            if isinstance(arg, Q):
                arg = q_from_request(deepcopy(arg))
            new_args.append(arg)
        return new_args

    def prepare_kwargs(self, kwargs, request):
        user = getattr(request, 'user', None)
        user_id = user.id if user else None

        new_kwargs = {}
        for k, v in kwargs.items():
            if v is CURRENT_USER:
                v = user_id
            new_kwargs[k] = v
        return new_kwargs


def quick_pagination(queryset, page, limit, max_limit=1000):
    """
    Функция быстрой паджинации для больших таблиц, не вызывающая count(*).
    """
    try:
        page = int(page)
    except ValueError:
        page = 1
    try:
        limit = int(limit)
        assert limit <= max_limit
    except ValueError:
        limit = 10
    except AssertionError:
        limit = max_limit
    offset = (page - 1) * limit
    queryset = queryset[offset:(offset + limit + 1)]
    result = queryset
    if len(result) > limit:
        has_next = True
        result = result[:limit]
    else:
        has_next = False
    return result, page, limit, has_next


def dictfetchall(cursor, aggregate=()):
    """
    Return all rows from a cursor as a dict.
    """
    columns = [col[0] for col in cursor.description]

    total = {col: 0 for col in aggregate}
    use_total = bool(total)
    total_keys = total.keys()

    def to_dict(row):
        d = dict(zip(columns, row))
        if use_total:
            for col in total_keys:
                total[col] += d[col]
        return d

    objects = [to_dict(row) for row in cursor.fetchall()]
    if total:
        return objects, total
    return objects


def get_object_or_none(klass, *args, **kwargs):
    """
    Возвращает объект или None, если объект не существует.

    klass может быть Model, Manager, или объектом QuerySet. Все остальные
    переданные параметры используются для запроса get().

    Замечание: Возвращает None, если найдено более одного объекта.
    """
    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        return None
    except queryset.model.MultipleObjectsReturned:
        return None


def pretty_sql(queryset):
    """Форматирует QuerySet в человекочитаемый SQL."""
    query = queryset.query
    compiler = query.get_compiler(queryset.db)
    with compiler.connection.schema_editor() as editor:
        sql, params = compiler.as_sql()
        value = sql % tuple(editor.quote_value(p) for p in params)
    return sqlparse.format(value, reindent=True, keyword_case='upper')
