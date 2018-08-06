#!/usr/bin/env python
from setuptools import setup, find_packages

with open('pagerduty/version.py') as version_file:
    exec(compile(version_file.read(), version_file.name, 'exec'))

options = {
    'name': 'pagerduty',
    'version': __version__,
    'packages': find_packages(),
    'scripts': [],
    'description': 'A python handler for PagerDuty API',
    'author': 'Jason Anderson',
    'author_email': 'darth.scrumlord@gmail.com',
    'maintainer': 'Jason Anderson',
    'maintainer_email': 'darth.scrumlord@gmail.com',
    'license': 'MIT',
    'url': 'https://github.com/Jazun713/sensu-plugin-py-pagerduty',
    'download_url': 'https://github.com/Jazun713/sensu-plugin-py-pagerduty/archive/master.tar.gz',
    'classifiers': [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    'install_requires': ['requests', 'six'],
    'tests_require': ['pep8','pylint'],
    'cmdclass': {}
}

setup(**options)