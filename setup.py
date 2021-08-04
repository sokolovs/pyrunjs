#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='pyrunjs',
    version='1.0.3',
    description='Python PyV8 JS wrapper',
    author='Sergey V. Sokolov',
    author_email='sergey.sokolov@air-bit.eu',
    url='https://github.com/sokolovs/pyrunjs',
    packages=find_packages(exclude=['examples']),
    package_data={'runjs': ['data/*.*']},
    install_requires=['pyduk @ git+https://git.air-bit.eu/airbit/pyduk@0.2.1',
                      'pyv8 @ git+https://git.air-bit.eu/airbit/pyv8@prebuilt-ubuntu-x64-0.2.1'],
    dependency_links=['git+https://git.air-bit.eu/airbit/pyduk@0.2.1#egg=pyduk',
                      'git+https://git.air-bit.eu/airbit/pyv8@prebuilt-ubuntu-x64-0.2.1#egg=pyv8'],
)
