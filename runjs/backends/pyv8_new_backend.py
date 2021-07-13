import json

from runjs.backends.exceptions import JSRuntimeException

try:
    import pyv8
    from pyv8 import *

    V8Initializer.get_instance()
except ImportError:
    pass
from runjs.backends.abstract import AbstractBackend


class PyV8NewBackend(AbstractBackend):
    """This backend uses new pyv8 implementation."""

    can_precompile = False
    can_run_str = False

    def _get_js_obj(self, obj):
        if hasattr(obj, '__dict__'):
            obj = dict(obj)
        return json.dumps(obj)

    def _run_unprotected(self, func=None, fargs=[]):
        instance = V8Instance()
        instance.run("var global = new Function('return this;')();")
        code = ''
        for k, v in self.js_global_vars.items():
            code += f'var {k} = {self._get_js_obj(v)};\n'

        for lib in self.js_libs:
            with open(lib) as f:
                code += f.read()

        for lib in self.js_libs_code.values():
            code += lib

        if func:
            code += f'{func}({",".join(map(self._get_js_obj, fargs))});\n'
            code += self.js_code
            ret = instance.run(code)
        return ret


    def run(self, func=None, fargs=None):
        """
        run js code with libraries and return result as
            python type

        :param str func: (optional) js function name
        :param list fargs: (optional) list of js function args

        :raise JSRuntimeException: js runtime error
        :raise RuntimeError
        """

        try:
            return self._run_unprotected(func, fargs)
        except IOError as err:
            raise RuntimeError from IOError
        except pyv8.V8Error as err:
            raise JSRuntimeException(str(err), err.traceback) from err
