import logging
from django.http import HttpResponse
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
logger = logging.getLogger(__name__)

class UserMiddlewere(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        url = request.path_info  
        if request.user.is_authenticated:
           
            if request.session.get('user'):
                if request.path == '/user/login' or request.path == '/user/login/':
                    return redirect('user:dashboard')
                else:
                    return self.get_response(request)
      
        else:    
            if url.startswith('/user/'):
                if request.path == '/user/login' or request.path == '/user/login/' or request.path == '/user/register' or request.path == '/user/register/':
                  return self.get_response(request)
                else: 
                  return redirect('user:login')
            else:
                return self.get_response(request)
