from django.core import meta
from django.models import auth

class PageView(meta.Model):
    user = meta.ForeignKey(auth.User, blank=True, null=True)
    # session
    ip_address = meta.IPAddressField()
    served = meta.DateTimeField(auto_now=True)
    url = meta.CharField(maxlength=512)
    referrer = meta.CharField(maxlength=512, blank=True, null=True)
    user_agent = meta.CharField(maxlength=512, blank=True, null=True)

    class META:
        admin = meta.Admin(
            list_display = ['url', 'served'],
            list_filter = ['url', 'served'],
        )

    def __repr__(self):
        return self.ip_address
