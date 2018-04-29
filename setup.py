from distutils.core import setup

from setuptools import find_packages

# variables

NAME = 'flaskpack'
VERSION = '0.1.10'

# end variables

def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]


install_reqs = parse_requirements(
    './requirements.txt')
reqs = [str(ir) for ir in install_reqs]

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
