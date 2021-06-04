import json

from pyv8 import *
from runjs.backends.abstract import AbstractBackend

V8Initializer.get_instance()

class PyV8NewBackend(AbstractBackend):
    can_precompile = False
    can_run_str = False

    def _get_js_obj(self, obj):
        if hasattr(obj, '__dict__'):
            obj = dict(obj)
        return json.dumps(obj)


    def run(self, func=None, fargs=[]):
        instance = V8Instance()
        instance.run("var global = new Function('return this;')();")
        code = ''
        for k, v in self.js_global_vars.items():
            code += f'var {k} = {self._get_js_obj(v)};\n';

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
