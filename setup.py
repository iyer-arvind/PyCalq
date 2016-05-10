#!/usr/bin/env python
from setuptools import setup

version = '0.0.1'
console_scripts = [
        'pycalq = pycalq.pycalq:main'
]

install_requires = ['numpy', 'scipy', 'pint', 'tabulate']


setup(name='PyCalq',
      version=version,
      description='Engineering calculator woth python',
      author='Arvind S Iyer',
      author_email='iyer.arvind.sundaram@gmail.com',
      license='BSD',
      keywords='Math',
      packages=['pycalq'],
      entry_points={'console_scripts': console_scripts},
      install_requires=install_requires
)
