# -*- coding: utf-8 -*-
import logging
from collections import OrderedDict

import PyV8

from .abstract import AbstractBackend
from .exceptions import ArgumentError, JSFunctionNotExists

__all__ = ['PyV8Backend', ]


class PyV8Backend(AbstractBackend):
    """ Backend class for PyV8 """
    logger = logging.getLogger(__name__)
    can_precompile = True
    can_run_str = True

    def run(
            self, func=None, fargs=[], precompil_only=False,
            compil_only=False):
        """
        Run JS code with libraries and return last operand result or
            `func` result if it present

        :param str func: (optional) JS function name
        :param list fargs: (optional) list of JS function args
        :param bool precompil_only: (optional) if true, then it will
            return precommiled data all JS code
        :param bool compil_only: (optional) if true, then it
            will compile the JS code and throw errors if they were

        :raise SyntaxError: JS syntax error
        :raise PyV8.JSError: JS runtime error (contain fields:
            name, message, scriptName, lineNum, startPos, endPos,
            startCol, endCol, sourceLine, stackTrace)
        """
        precompiled = OrderedDict()
        compiled = OrderedDict()

        with PyV8.JSLocker():
            with PyV8.JSContext() as js_context:
                self.logger.debug('Set JS global context class attributes')
                for k, v in self.js_global_vars.items():
                    self.logger.debug(
                        'Set attribute name=%s, value=%s' % (k, v))
                    # Convert to JS objects
                    setattr(
                        js_context.locals, k,
                        self._get_js_obj(js_context, v))

                with PyV8.JSEngine() as engine:
                    precompil_error = False
                    try:
                        for js_lib, js_code in self.js_libs_code.items():
                            self.logger.debug('Precompile JS lib: %s' % js_lib)
                            precompiled[js_lib] = engine.precompile(js_code)
                    except SyntaxError:
                        precompil_error = True

                    if not precompil_error and precompil_only:
                        return precompiled

                    for js_lib, js_code in self.js_libs_code.items():
                        self.logger.debug('Compile JS lib: %s' % js_lib)
                        cparams = dict(
                            source=self.js_libs_code[js_lib],
                            name=js_lib)
                        if js_lib in precompiled:
                            cparams['precompiled'] = precompiled[js_lib]
                        compiled[js_lib] = engine.compile(**cparams)
                    if compil_only:
                        return True

                    result = None
                    for js_lib, js_script in compiled.items():
                        self.logger.debug('Run JS lib: %s' % js_lib)
                        result = js_script.run()

                    if not func or type(func) != str:
                        return result

                    if fargs and not isinstance(fargs, (list, tuple)):
                        raise ArgumentError(
                            'The "fargs" must be list or tuple')

                    if func not in js_context.locals:
                        raise JSFunctionNotExists(
                            'Function "%s" not exists in JS context' % func)

                    # Convert to JS objects
                    for i in range(len(fargs)):
                        fargs[i] = self._get_js_obj(js_context, fargs[i])

                    # Convert to Python objects
                    return self._get_py_obj(
                        js_context,
                        js_context.locals[func](*fargs))

    def _get_js_obj(self, ctx, obj):
        """
        Convert Python object to JS object and return it
        :param PyV8.JSContext ctx: current JS context
        :param mixed obj: object for convert
        """
        if isinstance(obj, (list, tuple)):
            js_list = []
            for entry in obj:
                js_list.append(self._get_js_obj(ctx, entry))
            return PyV8.JSArray(js_list)
        elif isinstance(obj, dict):
            js_obj = ctx.eval('new Object();')
            for key in obj.keys():
                try:
                    js_obj[key] = self._get_js_obj(ctx, obj[key])
                except Exception, e:
                    if (not str(e).startswith('Python argument types in')):
                        raise
                    import unicodedata
                    nkey = unicodedata.normalize(
                        'NFKD', key).encode('ascii', 'ignore')
                    js_obj[nkey] = self._get_js_obj(ctx, obj[key])
            return js_obj
        else:
            return obj

    def _get_py_obj(self, ctx, obj, route=[]):
        """
        Convert JS object to Python object and return it
        :param PyV8.JSContext ctx: current JS context
        :param mixed obj: object for convert
        :param list route: key list for lookup
            in iterable objects (internal usage)
        """
        def access(obj, key):
            if key in obj:
                return obj[key]
            return None

        cloned = None
        if isinstance(obj, (list, tuple, PyV8.JSArray)):
            cloned = []
            num_elements = len(obj)
            for index in range(num_elements):
                elem = obj[index]
                cloned.append(self._get_py_obj(ctx, elem, route + [index]))
        elif isinstance(obj, (dict, PyV8.JSObject)):
            cloned = {}
            for key in obj.keys():
                cloned_val = None
                if type(key) == int:
                    val = None
                    try:
                        val = access(obj, str(key))
                    except KeyError:
                        pass
                    if val is None:
                        val = access(obj, key)
                    cloned_val = self._get_py_obj(ctx, val, route + [key])
                else:
                    cloned_val = self._get_py_obj(
                        ctx, access(obj, key), route + [key])
                cloned[key] = cloned_val
        elif isinstance(obj, (str, bytes)):
            cloned = obj.decode('utf-8')
        else:
            cloned = obj
        return cloned
