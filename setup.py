#!/usr/bin/env python
from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES
import os
import bh as app

VERSION = RELEASE = app.get_version()
NAME = app.NAME


for scheme in INSTALL_SCHEMES.values():
    scheme['data'] = scheme['purelib']

def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


def scan_dir( target, _packages=None, _data_files=None):
    packages = _packages or []
    data_files = _data_files or []
    for dir_path, dir_names, file_names in os.walk(target):
        # Ignore dir_names that start with '.'
        for i, dir_name in enumerate(dir_names):
            if dir_name.startswith('.'): del dir_names[i]
        if '__init__.py' in file_names:
            packages.append('.'.join(fullsplit(dir_path)))
        elif file_names:
            data_files.append([dir_path, [os.path.join(dir_path, f) for f in file_names]])
    return packages, data_files

packages, data_files = scan_dir('bh')

setup(
    name=NAME,
    version=RELEASE,
    url='https://github.com/saxix/django-buildhost',
    author='sax',
    author_email='sax@os4d.org',
    license='BSD',
    packages=packages,
    data_files=data_files,
    platforms=['any'],
    classifiers=[],
    long_description=open('README').read()
)
