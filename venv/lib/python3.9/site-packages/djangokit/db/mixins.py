#
# Copyright (c) 2018, Grigoriy Kramarenko
# All rights reserved.
# This file is distributed under the BSD 3-Clause License.
#
from djangokit.utils.deep import to_dict, from_dict


def _save(instance, save):
    if save is not False and hasattr(instance, 'save'):
        fields = set(['details'])
        if save is not True:
            fields = fields.union(save)
        instance.save(update_fields=fields)


class DetailsMixin:
    """Methods for model with JSON field `details`."""
    details = None

    def to_details(self, field, value, append_to_list=False, save=False):
        """
        Advanced setup details parts.

        Default NOT stored in the database. To change this
        behavior, you should pass a parameter `save is not False`.
        """
        self.details = to_dict(
            self.details, field=field, value=value,
            append_to_list=append_to_list,
        )
        _save(self, save)
        return self.details

    def from_details(self, field, default=None, update=False, delete=False,
                     save=False):
        """
        Advanced receiving/removing a portion of the details.

        When receiving can set the specified default value.
        Default NOT stored in the database. To change this
        behavior, you should pass a parameter `save is not False`.
        """
        value = from_dict(
            self.details, field=field, default=default, update=update,
            delete=delete,
        )
        _save(self, save)
        return value

    def set_details(self, details=None, save=False, **kwargs):
        """Simple installation details, or upgrade part details."""
        if details:
            self.details = details
        else:
            d = self.details or dict()
            d.update(kwargs)
            self.details = d
        _save(self, save)
        return self.details


class StateMixin:
    """
    Миксин необходим в первую очередь для проверки нового объекта в шаблонах.
    """

    @property
    def is_new_instance(self):
        return self._state.adding

    @property
    def model_state(self):
        return self._state
