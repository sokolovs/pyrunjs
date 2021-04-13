import json
import os

import pyduk

from .abstract import AbstractBackend

__all__ = ['PydukBackend']


class PydukBackend(AbstractBackend):
    """This backend uses pyduk."""

    def _get_js_obj(self, obj):
        if hasattr(obj, '__dict__'):
            obj = dict(obj)
        return json.dumps(obj)

    def _run_unprotected(self, func=None, fargs=None):
        ctx = pyduk.Context(pyduk.USE_GLOBAL_POLYFILL)
        for k, v in self.js_global_vars.items():
            ctx.run(f'var {k} = {self._get_js_obj(v)}')

        for js_lib in self.js_libs:
            js_lib = os.path.abspath(js_lib)
            with open(js_lib) as lib_file:
                ctx.run(lib_file.read())

        for _, lib_code in self.js_libs_code.items():
            ctx.run(lib_code)

        res = ctx.run(self.js_code)
        if func:
            args = ','.join(map(self._get_js_obj, fargs if fargs else []))
            res = ctx.run(f'{func}({args})')
        return res


    def run(self, func=None, fargs=None):
        """
        run js code with libraries and return result as
            python string or as dict

        :param str func: (optional) js function name
        :param list fargs: (optional) list of js function args

        :raise syntaxerror: js syntax error or runtime error
        """

        try:
            return self._run_unprotected(func, fargs)
        except IOError as err:
            raise RuntimeError from IOError
        except (pyduk.JSRuntimeError, pyduk.ConversionError) as err:
            raise SyntaxError from err
