"""
>>> from django.models.blog import posts
>>> from django.utils.timesince import timesince
>>> from datetime import datetime

>>> posts.get_object(pk=1).posted
datetime.datetime(1979, 7, 7, 23, 12)

>>> posts.get_list(listed__exact=True)
[<blog.Post 1>]

>>> browser.go('/')
>>> blurt = browser.soup.first('div', { 'class': 'blurt' })
>>> blurt.h1.a.string
'Hello, World!'
>>> blurt.first('p', { 'class': 'timestamp' })['title']
'July 7, 1979 23:12 CET'
>>> blurt.first('p', { 'class': 'timestamp' }).string == 'Posted %s ago' % timesince(datetime(1979, 7, 7))
True
"""
