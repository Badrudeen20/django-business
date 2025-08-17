from functools import wraps 
from django.shortcuts import redirect
from django.contrib import messages
from .models import *
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse,HttpResponseBadRequest
from django.utils.decorators import method_decorator



class RoleRequired:
    def __init__(self, module):
        self.module = module

    def __call__(self, view_class):
        # ✅ Properly decorate class-based view dispatch
        original_dispatch = view_class.dispatch

        @wraps(original_dispatch)
        def new_dispatch(view_instance, request, *args, **kwargs):
            auth = request.session.get('master')
            if not auth:
                return JsonResponse({"success": False, "message": "Not authenticated"}, status=403)
            kwargs['authId'] = auth['id']
            if auth.get('is_admin'):
                kwargs['roleIds'] = list(Access.objects.all().values_list('id', flat=True))
                kwargs['permission'] = ['View', 'Add', 'Edit', 'Delete']
                kwargs['module'] = list(Module.objects.values_list('module', flat=True))
                kwargs['access'] = True
                kwargs['isAdmin'] = True
            else:
                kwargs['roleIds'] = list(Access.objects.filter(user_id=auth['id']).values_list('role_id', flat=True))
                permissions = Permission.objects.filter(role_id__in=kwargs['roleIds'],permission__contains='View').select_related('modules')

                kwargs['permission'] = list(set(
                    p.strip() for perm in permissions.values_list('permission', flat=True) for p in perm.split(',')
                ))
                kwargs['module'] = [permission.modules.module for permission in permissions]
                
                if  self.module in kwargs['module']:
                    parentIds = list(permissions.filter(~Q(module_parent_id='')).values_list('module_parent_id', flat=True))
                    if parentIds:
                       kwargs['access'] = self.checkAccess(parentIds,kwargs['roleIds']) 
                    else:
                       kwargs['access'] = True   
                       
                else:
                    kwargs['access'] = False  
                    if self.module:
                        return JsonResponse({
                        "success": False,
                        "error":'Invalid Permission!'
                        }, status=200) 
                
                kwargs['isAdmin'] = False
                
            return original_dispatch(view_instance, request, *args, **kwargs)

        view_class.dispatch = new_dispatch
        return view_class

    def checkAccess(self, parentId,roleId):
        status = False
        def recurse(mId,rId):
            nonlocal status
            if mId and rId:
                permissions = Permission.objects.filter(modules_id__in=mId,role_id__in=rId)
                if permissions.exists():
                    mId = list(
                        permissions.filter(
                            Q(~Q(module_parent_id='')) | Q(module_parent_id__in=mId)
                        ).values_list('module_parent_id', flat=True)
                    )
                    status = True
                    recurse(mId,rId)
                else:
                    status = False 
        recurse(parentId,roleId)
        return status