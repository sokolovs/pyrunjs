#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='pyrunjs',
    version='1.0.2',
    description='Python PyV8 JS wrapper',
    author='Sergey V. Sokolov',
    author_email='sergey.sokolov@air-bit.eu',
    url='https://github.com/sokolovs/pyrunjs',
    packages=find_packages(exclude=['examples']),
    package_data={'runjs': ['data/*.*']},
    install_requires=[],
)
