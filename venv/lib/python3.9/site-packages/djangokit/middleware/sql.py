#
# Copyright (c) 2021, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
import logging
from sqlparse import format

from django.conf import settings
from django.db import connection, reset_queries


def logging_queries(get_response):
    """
    Выводит в лог SQL-запросы на уровне DEBUG.
    """

    logger = logging.getLogger(__name__)
    REINDENT = getattr(settings, 'PRETTY_SQL_REINDENT', False)

    def pretty_sql(sql):
        return format(sql, reindent=REINDENT, keyword_case='upper')

    def middleware(request):
        if settings.DEBUG:
            reset_queries()
            start_queries = len(connection.queries)

            response = get_response(request)

            end_queries = len(connection.queries)

            queries = []
            total_time = 0
            for i, query in enumerate(connection.queries):
                time = query['time']
                total_time += float(time)
                queries.append(
                    f"QUERY #{i + 1}. {time} seconds:\n"
                    f"{pretty_sql(query['sql'])}"
                )

            logger.debug(
                '%s %s -- %d database queries at %f seconds.\n\n%s\n',
                request.method,
                request.path,
                end_queries - start_queries,
                total_time,
                '\n\n'.join(queries)
            )
        else:
            response = get_response(request)

        return response

    return middleware
