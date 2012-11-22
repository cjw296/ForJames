#!/usr/bin/env python

from setuptools import setup, find_packages
import sys, os

version = '0.25'

setup(name='for_james',
      version=version,
      description="samples in tornado",
      long_description="""a hello world in tornado""",
      author='Peter Bunyan',
      author_email='pete@blueshed.co.uk',
      url='http://www.blueshed.co.uk/for_james',
      packages=find_packages('src',exclude=['*tests*']),
      package_dir = {'':'src'},
      include_package_data = True, 
      exclude_package_data = { '': ['tests/*'] },
      install_requires = [
        'setuptools',
        'tornado>=2.4',
        'sockjs-tornado',
        'sqlalchemy>=0.7.9'
      ],
      entry_points = {
      'console_scripts' : [
                           'publish_for_james = simple_publish.server:main',
                           'colour_server = simple_colour.server:main'
                           ]
      })