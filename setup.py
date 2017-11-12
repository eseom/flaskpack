# coding: utf-8

from __future__ import unicode_literals

from distutils.core import setup

from setuptools import find_packages

# variables

NAME = 'flask_wrapper'
VERSION = '1.0.0'

# end variables

from pip.req import parse_requirements

install_reqs = parse_requirements(
    './requirements.txt', session='hack')
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name=NAME,
    entry_points={
        # 'console_scripts': [
        #     ' = greemed.guni:main',
        # ],
    },
    install_requires=reqs,
    version=VERSION,
    include_package_data=True,
    packages=[t for t in find_packages() if t.startswith(NAME) or t.startswith('migrations')],
    author='Red',
    author_email='red@woorooroo.com',
)
