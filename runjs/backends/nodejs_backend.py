# -*- coding: utf-8 -*-
import json
import logging
import os
import os.path
import shutil
import subprocess

from tempfile import NamedTemporaryFile

from .abstract import AbstractBackend

logger = logging.getLogger(__name__)

__all__ = ['NodeJSBackend', ]


class NodeJSBackend(AbstractBackend):
    """ Backend class for Nodejs """
    logger = logging.getLogger(__name__)
    can_precompile = False
    can_run_str = False

    def run(self, func=None, fargs=[]):
        """
        Run JS code with libraries and return result as
            Python unicode string or as dict

        :param str func: (optional) JS function name
        :param list fargs: (optional) list of JS function args

        :raise SyntaxError: JS syntax error or runtime error
        """
        cdir = os.path.abspath(os.path.dirname(__file__) + '/../data')
        include_lib = cdir + '/include.js'

        script_code = ''
        if os.path.isfile(include_lib) and os.access(include_lib, os.R_OK):
            script_code = open(include_lib).read()
        else:
            err = 'Can not read: "%s" file' % include_lib
            self.logger.error(err)
            raise RuntimeError(err)

        for js_lib in self.js_libs:
            js_lib = os.path.abspath(js_lib)
            lib_exists = os.path.isfile(js_lib) and os.access(js_lib, os.R_OK)
            if not lib_exists:
                err = 'Can not read: "%s" file' % js_lib
                self.logger.error(err)
                raise RuntimeError(err)
            script_code += "include('%s');\n" % js_lib

        # Global vars
        if self.js_global_vars:
            script_code += '\n\n// ==== Global JS variables\n'
            for k, v in self.js_global_vars.items():
                script_code += 'var %s = %s;\n' % (k, self._get_js_obj(v))

        # Main script code
        script_code += '\n\n// ==== MAIN JS code\n'
        script_code += self.js_code
        script_code += '\n'

        # Convert to JS objects and create arguments string
        fargs_str = ''
        fargs_len = len(fargs)
        for i in range(fargs_len):
            fargs_str += self._get_js_obj(fargs[i])
            if i < fargs_len - 1:
                fargs_str += ', '

        if func is not None:
            func_call = 'var __func_call_res = %s(%s);\n'
            func_call += (
                'process.stdout.write(JSON.stringify(__func_call_res));\n')
            script_code += func_call % (func, fargs_str)

        logger.debug('JS source code:')
        logger.debug(script_code)

        # Write script code to file
        script_code_file = NamedTemporaryFile(delete=False, suffix='-main.js')
        script_code_file.write(script_code.encode())
        script_code_file.close()

        # Run script code
        result = None
        try:
            result = subprocess.check_output(
                ['nodejs', script_code_file.name], stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise SyntaxError(e.output.decode())
        finally:
            os.unlink(script_code_file.name)
            if self.js_libs_tmpdir is not None:
                shutil.rmtree(self.js_libs_tmpdir, ignore_errors=True)
        return self._get_py_obj(result)

    def _get_js_obj(self, obj):
        if hasattr(obj, '__dict__'):
            obj = dict(obj)
        return json.dumps(obj)

    def _get_py_obj(self, obj):
        result = obj
        try:
            result = json.loads(obj)
        except Exception:
            pass
        return result

    def can_precompile(self):
        return False
