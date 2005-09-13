"""A Vary-capable cache middleware. Adapted from Djangos cache
middleware."""

from django.conf import settings
from django.core.cache import cache
from django.utils.httpwrappers import HttpResponseNotModified
import datetime, md5

class CacheMiddleware:
    """
    Cache middleware. If this is enabled, each Django-powered page will be
    cached for CACHE_MIDDLEWARE_SECONDS seconds. Cache is based on URLs. Pages
    with GET or POST parameters are not cached.

    Pages will be cached based on the contents of the request headers
    listed in the response Vary-header [ FIXME -- need example, or better
    description? ]. This means that pages cannot change their Vary-header,
    without strange results.
    """
    def process_request(self, request):
        """Checks whether the page is already cached. If it is, returns
        the cached version."""

        if request.GET or request.POST:
            request._ibofobi_cache_update = False
            return None # Don't bother checking the cache.

        vary_key = 'ibofobi.cache.vary.%d.%s' % (settings.SITE_ID, request.path)
        request._ibofobi_cache_vary_key = vary_key

        page_key = 'ibofobi.cache.page.%d.%s' % (settings.SITE_ID, request.path)
        request._ibofobi_cache_page_key = page_key

        request._ibofobi_cache_varies = varies = cache.get(vary_key, None)
        response = None

        if varies:
            response_key = page_key
            for meta_key in varies:
                response_key = response_key + '.' + request.META.get(meta_key, '')
            request._ibofobi_cache_response_key = response_key
            response = cache.get(response_key, None)
        
        if response is None:
            request._ibofobi_cache_update = True
            return None
        else:
            request._ibofobi_cache_update = False
            #print >>df, 'Returning cached copy of %s' % response_key
            return response

    def process_response(self, request, response):
        """Sets the cache, if needed."""

        if not request._ibofobi_cache_update:
            return response

        #response['ETag'] = md5.new(content).hexdigest()
        #response['Last-Modified'] = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

        if request._ibofobi_cache_varies:
            response_key = request._ibofobi_cache_response_key
        else:
            varies = []
            response_key = request._ibofobi_cache_page_key
            if response.has_header('Vary'):
                vary = response['Vary']
                for header in vary.split(','):
                    header = header.strip()
                    meta_key = 'HTTP_' + header.upper().replace('-', '_')
                    response_key = response_key + '.' + request.META.get(meta_key, '')
                    varies.append(meta_key)

            cache.set(request._ibofobi_cache_vary_key, varies,
                      settings.CACHE_MIDDLEWARE_SECONDS)

        #print >>df, 'Updating cached copy of %s' % response_key
        cache.set(response_key, response,
                  settings.CACHE_MIDDLEWARE_SECONDS)

        return response
