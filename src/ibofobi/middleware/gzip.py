import re
from django.utils.text import compress_string

re_vary_accept = re.compile(r'\bAccept-Encoding\b')
re_accepts_gzip = re.compile(r'\bgzip\b')

class GZipMiddleware:
    def process_response(self, request, response):
        if response.has_header('Vary'):
            if not re_vary_accept.search(response['Vary']):
                response['Vary'] = response['Vary'] + ', Accept-Encoding'
        else:
            response['Vary'] = 'Accept-Encoding'

        # FIXME -- Shouldn't Content-Encoding be Content-Transfer-Encoding?!
        if response.has_header('Content-Encoding'):
            return response

        ae = request.META.get('HTTP_ACCEPT_ENCODING', '')
        if not re_accepts_gzip.search(ae):
            return response

        response.content = compress_string(response.content)
        response['Content-Encoding'] = 'gzip'

        return response
