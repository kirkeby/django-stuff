#!/usr/bin/env python

from setuptools import setup

setup(name = "ibofobi",
      author = "Sune Kirkeby",
      url = "http://ibofobi.dk/stuff/ibofobi",
      version = '0.1',
      packages = ['ibofobi', 'ibofobi.apps',
                  'ibofobi.middleware', 'ibofobi.utils'],
      namespace_packages = ['ibofobi.apps'],
      package_dir = {'': 'src'},
      zip_safe = True,
)
setup(name = "blog",
      author = "Sune Kirkeby",
      url = "http://ibofobi.dk/stuff/ibofobi",
      version = '0.1',
      packages = ['ibofobi', 'ibofobi.apps', 'ibofobi.apps.blog',
                  'ibofobi.apps.blog.models', 'ibofobi.apps.blog.views',
                  'ibofobi.apps.blog.templatetags',
                  'ibofobi.apps.blog.urls'],
      namespace_packages = ['ibofobi.apps'],
      package_dir = {'': 'src'},
      package_data = {'ibofobi.apps.blog': ['templates/blog/*.html',
                                            'templates/blog/*.xml',],},
      zip_safe = True,
)
