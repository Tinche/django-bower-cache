# -*- coding: utf-8 -*-
#!/usr/bin/env python

import os
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


VERSION = '0.4.2'

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    print("You probably want to also tag the version now:")
    print(" git tag -a %s -m 'version %s'" % (VERSION, VERSION))
    print(" git push --tags")
    sys.exit()

with open('README.md') as f: readme = f.read()

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['test_registry']
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


class Coverage(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['test_registry']
        self.test_suite = True

    def run_tests(self):
        import coverage
        import pytest
        cov = coverage.coverage()
        cov.start()
        errno = pytest.main(self.test_args)
        cov.stop()
        cov.save()
        cov.report()
        sys.exit(errno)

install_requires = [
    'Django >= 1.6, < 1.7',
    'djangorestframework >= 2.3.12, < 3.0',
    'envoy >= 0.0.3',
    'requests >= 2.3.0, < 2.6.0',
    'celery >= 3.1.11, < 3.2',
]

tests_require = [
    'pytest-django',
    'coverage',
    'beautifulsoup4',
    'django-celery',
]

extras_require = {
    ':python_version == "2.6" or python_version == "2.7"': ['configparser==3.3.0post2']
}

if sys.version_info[0] == 2:
    tests_require.append('mock==1.0.1')

setup(
    name='django-bower-cache',
    version=VERSION,
    description='A Django app implementing a local caching proxy for Bower packages.',
    long_description=readme + '\n\n',
    author='Tin Tvrtkovic',
    author_email='tinchester@gmail.com',
    url='https://github.com/tinche/django-bower-cache',
    packages=['registry'],
    include_package_data=True,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require,
    cmdclass={'test': PyTest, 'coverage': Coverage},
    license="MIT",
    zip_safe=False,
    keywords='bower',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
