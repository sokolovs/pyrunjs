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
    install_requires=['pyduk @ git+https://github.com/ConsonantSpork/pyduk@0.1.2',
                      'pyv8 @ git+https://github.com/ConsonantSpork/pyv8@prebuilt-ubuntu-x64-0.1.2'],
    dependency_links=['git+https://github.com/ConsonantSpork/pyduk@0.1.2#egg=pyduk',
                      'git+https://github.com/ConsonantSpork/pyv8@prebuilt-ubuntu-x64-0.1.2#egg=pyv8'],
)
