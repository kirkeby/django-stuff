from django.core.template_loader import get_template
from django.core.template import Context

from django.models.aggemam import posts
from django.models.auth import users

template = get_template('aggemam/email')

for user in users.get_list():
    for post in posts.get_unread_for_user(user):
        post.add_userpostmarks(user, 'rd')
        print template.render(Context({ 'user': user, 'post': post }))
        break