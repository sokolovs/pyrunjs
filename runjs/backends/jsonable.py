# -*- coding: utf-8 -*-
# !!! Note: the object must be converted to a dictionary before
# !!! JSON serialization
import decimal
from datetime import date, datetime, time


__all__ = ('Jsonable', )


class Jsonable(object):
    """ Mixin for JSONable objects """
    def __iter__(self):
        merged = self.__class__.__dict__.copy()
        merged.update(self.__dict__)
        for attr, value in merged.items():
            if attr.startswith('_'):
                continue
            if callable(getattr(self, attr)):
                continue
            yield attr, self.value_to_json(value)

    @staticmethod
    def value_to_json(value):
        if isinstance(value, str):
            return value
        elif isinstance(value, (date, datetime, time)):
            return value.isoformat()
        elif type(value).__name__ in ('property', 'cached_property'):
            return value.__get__(value, value.__class__)
        elif isinstance(value, decimal.Decimal):
            return str(value)
        elif hasattr(value, '__iter__'):
            if isinstance(value, (list, tuple)):
                a = []
                for subval in value:
                    a.append(Jsonable.value_to_json(subval))
                return a
            else:
                dv = dict(value)
                d = {}
                for k in dv:
                    d[k] = Jsonable.value_to_json(dv[k])
                return d
        else:
            return value
