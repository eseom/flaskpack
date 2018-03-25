from distutils.core import setup

from setuptools import find_packages

# variables

NAME = 'flaskpack'
VERSION = '0.1.4'

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
    packages=[t for t in find_packages() if
              t.startswith(NAME) or t.startswith('migrations')],
    include_package_data=True,
    # package_data={
    # 	'flaskpack': ['flaskpack/static/swagger/*'],
    # },
    author='Red',
    author_email='red@woorooroo.com',
)
