Python wrapper for PyV8 and NodeJS.
The library provides an interface un JS code in Python (optional: precompile and compile with PyV8)

### Install:
```
pip install --upgrade git+https://github.com/sokolovs/pyrunjs.git
```

### Example:
```python
# -*- coding: utf-8 -*-
from runjs import *
from runjs.backends.jsonable import Jsonable

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

if (typeof module !== "undefined" && module.exports) {
    module.exports = {
        hello_value: hello_value,
        hello_list: hello_list,
        hello_dict: hello_dict,
        hello_object: hello_object
    };
} else if (typeof global !== "undefined") {
    global.hello_value = hello_value;
    global.hello_list = hello_list;
    global.hello_dict = hello_dict;
    global.hello_object = hello_object;
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


class ExampleObject(Jsonable):
    field1 = 123456
    field2 = [1, 2, 3, 4, 5, 6, 7]
    field3 = {'key1': 'value1', 'key2': 'value2'}

    def __init__(self):
        self.field4 = 654321
        self.field5 = [8, 9, 10, 11, 12]
        self.field6 = {'key6': 'value6', 'key7': 'value7'}

    @property
    def test_property_method(self):
        return True

    def test_method(self):
        """ Warning: not serialized! """
        return False

exo = ExampleObject()

js = JSRunWrapper.factory(
    backend='pyv8',  # or backend='nodejs',
    js_code=js_code,
    # js_libs=['/path/to/mylib.js', '/path/to/lib2.js'],
    js_libs_code={'mylib.js': js_lib_code})

# Set global context variables
js.set_global_var('gvar1', 1)
js.set_global_var('gvar2', [5, 6, 7, 8, 9])
js.set_global_var('gvar3', {'key3': 'value3', 'key4': 'value4'})
js.set_global_var('gvar4', exo)

# Call JS functions
print js.run(func='hello_value', fargs=[125])
print js.run(func='hello_list', fargs=[[10, 11, 12, 13, 14, 15, 16], ])
print js.run(func='hello_dict', fargs=[{'key4': 'value4', 'key5': 'value5'}, ])
print js.run(func='hello_object', fargs=[exo, ])
print js.run(func='global_example1')
print js.run(func='global_example2')
print js.run(func='global_example3')
print js.run(func='global_example4')
```
