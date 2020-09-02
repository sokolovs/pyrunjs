# -*- coding: utf-8 -*-
from runjs import *

js_lib_code = '''
function hello_value(v) {
    return v + 5;
}

function hello_list(l) {
    var sum = 0;
    for (i = 0; i < l.length; i++) {
        sum += l[i];
    }
    return sum;
}

function hello_dict(d) {
    return Object.keys(d);
}

function hello_object(o) {
    return Object.keys(o);
}
'''

js_code = '''
function global_example1() {
    return hello_value(gvar1);
}

function global_example2() {
    return hello_list(gvar2);
}

function global_example3() {
    return hello_dict(gvar3);
}

function global_example4() {
    return hello_object(gvar4);
}
'''


class ExampleObject(object):
    field1 = 123456
    field2 = [1, 2, 3, 4, 5, 6, 7]
    field3 = {'key1': 'value1', 'key2': 'value2'}

exo = ExampleObject()

js = JSRunWrapper(
    js_code,
    js_libs=['/path/to/mylib.js', '/path/to/lib2.js'],
    js_libs_code={'mylib.js': js_lib_code})

# Set global context variables
js.set_global_var('gvar1', 1)
js.set_global_var('gvar2', [5, 6, 7, 8, 9])
js.set_global_var('gvar3', {'key3': 'value3', 'key4': 'value3'})
js.set_global_var('gvar4', exo)

# Call JS functions
print js.run(func='hello_value', args=[125])
print js.run(func='hello_list', args=[[10, 11, 12, 13, 14, 15, 16], ])
print js.run(func='hello_dict', args=[{'key4': 'value5', 'key5': 'value5'}, ])
print js.run(func='hello_object', args=[exo, ])
print js.run(func='global_example1')
print js.run(func='global_example2')
print js.run(func='global_example3')
print js.run(func='global_example4')
