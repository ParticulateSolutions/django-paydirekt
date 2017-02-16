#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import re
import os
import sys


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.match("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]

def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if 'tests' not in dirnames and not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}

REQUIREMENTS = [
    'Django>=1.8'
]

version = get_version('django_paydirekt')


if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    print("You probably want to also tag the version now:")
    print("  git tag -a %s -m 'version %s'" % (version, version))
    print("  git push --tags")
    sys.exit()


setup(
    name='django-paydirekt',
    author='Particulate Solutions GmbH',
    author_email='tech@particulate.me',
    description=u'Django integration of Paydirekt.de',
    version=version,
    url='https://github.com/ParticulateSolutions/django-paydirekt',
    packages=get_packages('django_paydirekt'),
    package_data=get_package_data('django_paydirekt'),
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Framework :: Django',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    install_requires=REQUIREMENTS,
    zip_safe=False)
