# -*- coding: utf-8 -*-
import logging

from .backends import NodeJSBackend, PyV8Backend

logger = logging.getLogger(__name__)

__all__ = ['JSRunWrapper', ]


class JSRunWrapper(object):
    """ Backend factory class """

    @staticmethod
    def factory(backend='pyv8', js_code='', js_libs=[], js_libs_code={}):
        if backend == 'nodejs':
            return NodeJSBackend(js_code, js_libs, js_libs_code)
        elif backend == 'pyv8':
            return PyV8Backend(js_code, js_libs, js_libs_code)
        raise ValueError('Invalid backend passed to `factory()`')
