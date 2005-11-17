"""
>>> from django.models.auth import users
>>> user = users.create_user('me', 'John', 'Doe')
>>> user.save()

>>> first_post.title
'First Post!'
>>> first_post.fetched is None
False
>>> first_post.get_preferred_link().href
'http://example.com/post/'

>>> first_post.add_userpostmark(user, 'rd')
"""
