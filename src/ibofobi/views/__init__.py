import django.views.core.flatfiles
def flatfile(request, path):
    """I proxy django.views.core.flatfiles.flat_file setting the
    content-type to XHTML."""
    resp = django.views.core.flatfiles.flat_file(request, path)
    resp['Content-Type'] = 'application/xhtml+xml; charset=utf-8'
    return resp
