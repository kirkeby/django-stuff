# Copyright 2005 (C) Sune Kirkeby -- Licensed under the "X11 License"

from django.core import meta

class Person(meta.Model):
    email = meta.EmailField('e-mail')
    name = meta.CharField('full name', maxlength=117)

    class META:
        admin = meta.Admin(
            fields = (
                (None, {'fields': ('email', 'name'),}),
            )
        )

    def __repr__(self):
        return self.name

class Account(meta.Model):
    name = meta.CharField('account name', maxlength=117)
    #meta.SlugField('slug', 'account slug'),
    path = meta.SlugField('account sluf')
    open = meta.BooleanField('accepts now posts')
    members = meta.ManyToManyField(Person, related_name='member')

    class META:
        admin = meta.Admin(
            fields = (
                (None, {'fields': ('name', 'path', 'open'),}),
                (None, {'fields': ('members',)}),
            )
        )

    def __repr__(self):
        return self.name

class Post(meta.Model):
    account = meta.ForeignKey(Account)
    depositor = meta.ForeignKey(Person)
    when = meta.DateField('date of event')
    description = meta.CharField('description of event', maxlength=117)

    class META:
        admin = meta.Admin(
            fields = (
                (None, {'fields': ('account', 'depositor')}),
                ('Post', {'fields': ('when', 'description')}),
            )
        )

    def __repr__(self):
        return '%s, %r, %s' % (self.when, self.get_depositor(), self.description)

class Invoice(meta.Model): # Punishment?
    post = meta.ForeignKey(Post)
    victim = meta.ForeignKey(Person)
    amount = meta.FloatField(max_digits=11, decimal_places=2)

    class META:
        admin = meta.Admin(
            fields = (
                (None, {'fields': ('post', 'victim', 'amount')}),
            )
        )

    def __repr__(self):
        p = self.get_post()
        return '%s %s -- %r -> %r %+.2f' % (p.when, p.description,
                                            p.get_depositor(),
                                            self.get_victim(), -self.amount)
