from django.conf import settings

class TemplateDirsHacker:
    """I am an ugly hack for Django developers, depending on the requested
    URL I munge django.conf.settings.TEMPLATE_DIRS! Beware of my l33t
    eviln3ss! *Hrm* Sorry."""

    def process_request(self, request):
        for prefix, template_dirs in settings.TEMPLATE_DIRS_MAPPING:
            if request.path.startswith(prefix):
                settings.TEMPLATE_DIRS[:] = template_dirs[:]
                break
        else:
            raise AssertionError, 'no TEMPLATE_DIRS found'
