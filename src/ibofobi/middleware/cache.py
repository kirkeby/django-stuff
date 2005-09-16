"""A Vary-capable cache middleware. Adapted from Djangos cache
middleware."""

from django.conf import settings
from django.core.cache import cache
from django.utils.httpwrappers import HttpResponseNotModified

import datetime
import copy
import md5

class CacheMiddleware:
    """
    Cache middleware. If this is enabled, each Django-powered page will be
    cached for CACHE_MIDDLEWARE_SECONDS seconds. Cache is based on URLs.

    Only parameter-less GET or HEAD-requests are cached.

    Only responses with status-code 200 will be cached.

    This middleware expects that a HEAD request is answered with a
    response exactly like the corresponding GET request.

    When a hit occurs, a shallow copy of the original response object is
    returned from process_request.

    Pages will be cached based on the contents of the request headers
    listed in the response Vary-header [ FIXME -- need example, or better
    description? ]. This means that pages cannot change their Vary-header,
    without strange results.

    Also, this middleware sets ETag, Last-Modified, Expires and
    Cache-Control headers on the response object.
    """
    def process_request(self, request):
        """Checks whether the page is already cached. If it is, returns
        the cached version."""

        method = request.META['REQUEST_METHOD']
        if not method in ('GET', 'HEAD') or request.GET:
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
            return copy.copy(response)

    def process_response(self, request, response):
        """Sets the cache, if needed."""

        if not request._ibofobi_cache_update:
            return response
        if not request.META['REQUEST_METHOD'] == 'GET':
            # This is a stronger requirement than above. It is needed
            # because of interactions between this middleware and the
            # HTTPMiddleware, which throws the body of a HEAD-request
            # away before this middleware gets a chance to cache it.
            return response
        if not response.status_code == 200:
            return response

        now = datetime.datetime.utcnow()
        expires = now + datetime.timedelta(0, settings.CACHE_MIDDLEWARE_SECONDS)

        if not response.has_header('ETag'):
            response['ETag'] = md5.new(response.content).hexdigest()
        if not response.has_header('Last-Modified'):
            response['Last-Modified'] = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        if not response.has_header('Expires'):
            response['Expires'] = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
        if not response.has_header('Cache-Control'):
            response['Cache-Control'] = 'max-age=%d' % settings.CACHE_MIDDLEWARE_SECONDS

        if request._ibofobi_cache_varies:
            varies = request._ibofobi_cache_varies
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
