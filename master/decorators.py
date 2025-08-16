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
            
            if auth.get('is_admin'):
                kwargs['roleIds'] = list(Access.objects.all().values_list('id', flat=True))
                kwargs['permission'] = ['View', 'Add', 'Edit', 'Delete']
                kwargs['module'] = list(Module.objects.filter(module=self.module).values_list('module', flat=True))
                kwargs['access'] = True
                kwargs['isAdmin'] = True
            else:
               pass

            # ✅ Call original dispatch with view_instance
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