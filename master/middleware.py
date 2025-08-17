import logging
from django.http import HttpResponse
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
logger = logging.getLogger(__name__)

class MasterMiddlewere(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        url = request.path_info  
        if request.user.is_authenticated:
            
            if request.session.get('master'):
                if request.path == '/master/signin/' or request.path == '/master/signin':
                    return redirect('master:dashboard')
                else:
                    return self.get_response(request)
      
        else:    
            if url.startswith('/master/'):
                if request.path == '/master/signin' or request.path == '/master/signin/':
                    return self.get_response(request)
                else: 
                    return redirect('master:signin')
            else:
                return self.get_response(request)