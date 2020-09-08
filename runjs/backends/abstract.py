# -*- coding: utf-8 -*-
import logging
import os
import os.path
import tempfile

from collections import OrderedDict

from .exceptions import ArgumentError

__all__ = ['AbstractBackend', ]


class AbstractBackend(object):
    """ Abstract class for run JS backend """
    logger = logging.getLogger(__name__)
    can_precompile = False  # the backend can precompile
    can_run_str = False  # the backend can execute code from string

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
            self.logger.error(err)
            raise ArgumentError(err)

        if not isinstance(js_libs_code, dict):
            err = 'The `js_libs_code` argument must be dict'
            self.logger.error(err)
            raise ArgumentError(err)

        if self.can_run_str:
            for lib_file in self.js_libs:
                lib_file = os.path.abspath(lib_file)
                if os.path.isfile(lib_file) and os.access(lib_file, os.R_OK):
                    lib_code = open(lib_file).read()
                    self.js_libs_code[os.path.basename(lib_file)] = lib_code
                else:
                    self.logger.error(
                        'Can not read JS library file: %s' % lib_file)

            for js_lib, js_code in js_libs_code.items():
                self.js_libs_code[js_lib] = js_code
        else:
            # Write libs to files
            for js_lib, js_code in js_libs_code.items():
                tmpdir = tempfile.mkdtemp()
                js_lib_path = tmpdir + '/' + js_lib
                js_lib_file = open(js_lib_path, 'w')
                js_lib_file.write(js_code)
                js_lib_file.close()
                self.js_libs.append(js_lib_path)

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
            self.logger.error(err)
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
            self.logger.error(err)
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

    def run(self, *args, **kwargs):
        raise NotImplementedError('Subclasses must override `run()`')
