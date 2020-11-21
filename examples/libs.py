# -*- coding: utf-8 -*-
from runjs import *

js_code = '''
function decode_cbor() {
    var data = 'jRgeGl9SAAQaAALMLBoAV++uGgA816oYZAEYGhgaGBsYPQYD';
    var encoded = Base64Binary.decodeArrayBuffer(data);
    var decoded = CBOR.decode(encoded);
    return decoded;
}
'''

js = JSRunWrapper.factory(
    backend='nodejs',
    js_code=js_code,
    js_libs=['./base64-binary.js', './cbor.js'])

# Call JS functions
print(js.run(func='decode_cbor'))
