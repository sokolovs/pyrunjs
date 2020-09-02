# -*- coding: utf-8 -*-
import logging
import os
import os.path

from collections import OrderedDict

import PyV8

from .exceptions import ArgumentError, JSFunctionNotExists

logger = logging.getLogger(__name__)

__all__ = ['JSEvalWrapper', ]


class JSEvalWrapper(object):
    """ Wrapper class for PyV8 """

    def __init__(self, js_code='', js_libs=[], js_libs_code={}):
        """
        Create new JS wrapper
        :param str js_code: (optional) JS code for run
        :param list js_libs: (optional) paths to JS libraries code
        :param dict js_libs_code: (optional) dict of JS libraries code
            `key` is library name (ex: library.js)
            `value` is source code
        """
        self.js_code = js_code
        self.js_libs = js_libs
        self.js_libs_code = OrderedDict()
        self.js_global_vars = OrderedDict()

        if not isinstance(self.js_libs, (list, tuple)):
            err = 'The `js_libs` argument must be list or tuple'
            logger.error(err)
            raise ArgumentError(err)

        if not isinstance(js_libs_code, dict):
            err = 'The `js_libs_code` argument must be dict'
            logger.error(err)
            raise ArgumentError(err)

        for lib_file in js_libs:
            if os.path.isfile(lib_file) and os.access(lib_file, os.R_OK):
                lib_code = open(lib_file).read()
                self.js_libs_code[os.path.basename(lib_file)] = lib_code
            else:
                logger.error('Can not read JS library file: %s' % lib_file)

        for js_lib, js_code in js_libs_code.items():
            self.js_libs_code[js_lib] = js_code

        if self.js_code:
            self.js_libs_code['main'] = self.js_code

    def set_global_vars(self, js_vars):
        """
        Set variables for pass to JS global context
        :param dict vars: variables to pass
        :rtype: bool
        """
        if not isinstance(js_vars, dict):
            err = 'The `js_vars` argument must be dict'
            logger.error(err)
            raise ArgumentError(err)
        for k in js_vars.keys():
            self.js_global_vars[k] = js_vars[k]
        return True

    def delete_global_vars(self, js_vars):
        """
        Delete variables for pass to JS global context
        :param list|tuple vars: variables name for deleting
        """
        if not isinstance(js_vars, (list, tuple)):
            err = 'The `js_vars` argument must be list or tuple'
            logger.error(err)
            raise ArgumentError(err)
        for k in js_vars:
            del self.js_global_vars[k]
        return True

    def set_global_var(self, name, value):
        """
        Set variable for pass to JS global context
        :param str name: variable name
        :param str value: value
        """
        js_vars = dict()
        js_vars[name] = value
        return self.set_global_vars(js_vars)

    def delete_global_var(self, name):
        """
        Delete variable for pass to JS global context
        :param str name: variable name for deleting
        """
        return self.delete_global_vars((name, ))

    def run(self, func=None, args=[], precompil_only=False, compil_only=False):
        """
        Run JS code with libraries and return last operand result or
            `func` result if it present

        :param str func: (optional) JS function name
        :param list args: (optional) list of JS function args
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
                logger.debug('Set JS global context class attributes')
                for k, v in self.js_global_vars.items():
                    logger.debug('Set attribute name=%s, value=%s' % (k, v))
                    # Convert to JS objects
                    setattr(
                        js_context.locals, k,
                        self._get_js_obj(js_context, v))

                with PyV8.JSEngine() as engine:
                    precompil_error = False
                    try:
                        for js_lib, js_code in self.js_libs_code.items():
                            logger.debug('Precompile JS lib: %s' % js_lib)
                            precompiled[js_lib] = engine.precompile(js_code)
                    except SyntaxError:
                        precompil_error = True

                    if not precompil_error and precompil_only:
                        return precompiled

                    for js_lib, js_code in self.js_libs_code.items():
                        logger.debug('Compile JS lib: %s' % js_lib)
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
                        logger.debug('Run JS lib: %s' % js_lib)
                        result = js_script.run()

                    if not func or type(func) != str:
                        return result

                    if args and not isinstance(args, (list, tuple)):
                        raise ArgumentError(
                            'The function "args" must be list or tuple')

                    if func not in js_context.locals:
                        raise JSFunctionNotExists(
                            'Function "%s" not exists in JS context' % func)

                    # Convert to JS objects
                    for i in range(len(args)):
                        args[i] = self._get_js_obj(js_context, args[i])

                    # Convert to Python objects
                    return self._get_py_obj(
                        js_context,
                        js_context.locals[func](*args))

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
        elif type(obj) == str:
            cloned = obj.decode('utf-8')
        else:
            cloned = obj
        return cloned
