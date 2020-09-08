# -*- coding: utf-8 -*-
import decimal
from datetime import date, datetime, time


class Jsonable(object):
    """ Mixin for JSONable objects """
    def __iter__(self):
        merged = self.__class__.__dict__.copy()
        merged.update(self.__dict__)
        for attr, value in merged.iteritems():
            if attr.startswith('_'):
                continue
            if callable(getattr(self, attr)):
                continue
            if isinstance(value, (date, datetime, time)):
                iso = value.isoformat()
                yield attr, iso
            elif type(value).__name__ in ('property', 'cached_property'):
                yield attr, value.__get__(value, value.__class__)
            elif isinstance(value, decimal.Decimal):
                yield attr, str(value)
            elif hasattr(value, '__iter__'):
                if hasattr(value, 'pop'):
                    a = []
                    for subval in value:
                        if hasattr(subval, '__iter__'):
                            a.append(dict(subval))
                        else:
                            a.append(subval)
                    yield attr, a
                else:
                    yield attr, dict(value)
            else:
                yield attr, value
