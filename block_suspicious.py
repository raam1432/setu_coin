from django.http import HttpResponseNotFound

class BlockSuspiciousPathsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.blocked_paths = ['/wp-admin/', '/wp-login.php', '/xmlrpc.php']

    def __call__(self, request):
        for path in self.blocked_paths:
            if request.path.startswith(path):
                return HttpResponseNotFound("Not Found")
        return self.get_response(request)