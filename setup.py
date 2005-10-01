#!/usr/bin/env python

from setuptools import setup

setup(name = "ibofobi",
      author = "Sune Kirkeby",
      url = "http://ibofobi.dk/stuff/ibofobi",
      packages = ['ibofobi', 'ibofobi.apps',
                  'ibofobi.middleware', 'ibofobi.utils'],
      namespace_packages = ['ibofobi.apps'],
      package_dir = {'': 'src'},
)
setup(name = "blog",
      author = "Sune Kirkeby",
      url = "http://ibofobi.dk/stuff/ibofobi",
      packages = ['ibofobi', 'ibofobi.apps', 'ibofobi.apps.blog',
                  'ibofobi.apps.blog.models', 'ibofobi.apps.blog.views',
                  'ibofobi.apps.blog.templatetags',
                  'ibofobi.apps.blog.urls'],
      namespace_packages = ['ibofobi.apps'],
      package_dir = {'': 'src'},
      package_data = {'ibofobi.apps.blog': ['templates/blog/*.html',
                                            'templates/blog/*.xml',],},
)
