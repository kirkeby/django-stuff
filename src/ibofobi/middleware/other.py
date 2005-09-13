import re

re_vary_cookie = re.compile(r'\bCookie\b')

class FixVaryHeaderMiddleware:
    def process_response(self, request, response):
        if response.has_header('Vary'):
            if not re_vary_cookie.search(response['Vary']):
                response['Vary'] = response['Vary'] + ', Cookie'
        else:
            response['Vary'] = 'Cookie'
        return response
