from master.middleware import MasterMiddlewere
from user.middleware import UserMiddlewere
class ConditionalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.master_middleware = MasterMiddlewere(get_response)
        self.project_middleware = UserMiddlewere(get_response)

    def __call__(self, request):
        path = request.path

        if path.startswith('/master/'):
            return self.master_middleware(request)
        
        if path.startswith('/user/'):
            return self.project_middleware(request)

        # Default path - no custom middleware
        return self.get_response(request)