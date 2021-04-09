# -*- coding: utf-8 -*-
import logging

from .backends import NodeJSBackend, PyV8Backend, PydukBackend

logger = logging.getLogger(__name__)

__all__ = ['JSRunWrapper', ]


class JSRunWrapper(object):
    """ Backend factory class """

    @staticmethod
    def factory(backend='pyv8', js_code='', js_libs=[], js_libs_code={}):
        """
        Create instance

        :param str backend: (optional) backend name ('pyv8', 'v8' or 'nodejs')
        :param str js_code: (optional) main source code
        :param list js_libs: (optional) list of paths to files with libraries
        :param dict js_libs_code: (optional) dict of libraries code, key is
            library name (ex: lib.js), value is source code

        :raise ValueError: invalid backend
        """
        if backend == 'nodejs':
            return NodeJSBackend(js_code, js_libs, js_libs_code)
        elif backend == 'pyv8':
            return PyV8Backend(js_code, js_libs, js_libs_code)
        elif backend == 'pyduk':
            return PydukBackend(js_code, js_libs, js_libs_code)
        raise ValueError('Invalid backend passed to `factory()`')
