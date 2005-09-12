import re

re_ct_xhtml = re.compile(r'^application/xhtml\+xml\b')
re_accept_xhtml = re.compile(r'\bapplication/xhtml\+xml\b')

class XHTMLAsHTMLMiddleware:
    """I change content-type application/xhtml+xml into text/html, if the
    browser does not support the XHTML content-type."""

    def process_response(self, request, response):
        if re_ct_xhtml.match(response['Content-Type']):
            accept = request.META.get('HTTP_ACCEPT', '')
            if not re_accept_xhtml.search(accept):
                ct = response['Content-Type']
                ct = ct.replace('application/xhtml+xml', 'text/html')
                response['Content-Type'] = ct

            if response.has_header('Vary'):
                response['Vary'] = response['Vary'] + ', Accept'
            else:
                response['Vary'] = 'Accept'

        return response
