#!/usr/bin/env python
from distutils.core import setup

setup(
    name='pyrunjs',
    version='1.0.0',
    description='Python PyV8 JS wrapper',
    author='Sergey V. Sokolov',
    author_email='sergey.sokolov@air-bit.eu',
    url='https://github.com/sokolovs/pyrunjs',
    packages=['runjs'],
    install_requires=['PyV8'],
)
