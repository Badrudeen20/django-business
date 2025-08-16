from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User 
from django.views import View
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.contrib import messages
from master.models import *
from user.models import *
from django.conf import settings
import json
from master.decorators import (
   RoleRequired
)

class Signin(TemplateView):
    template_name = 'master/signin.html'
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        user = request.POST['user']
        password = request.POST['password']
        user_obj = User.objects.using('default').filter(Q(username=user) | Q(email=user)).first()

        if user_obj:
            username = user_obj.username
            user = authenticate(request, username=username , password=password)
            if user is None:
                return JsonResponse({
                    "success": False,
                    "data":"Invalid Credentials!"
                }, status=200) 
            else:
                login(request, user)
                request.session['master'] = json.loads(
                    json.dumps({
                            'id': user.id,
                            'username': user.username,
                            'email': user.email,
                            'is_admin':user.is_superuser
                    }, cls=DjangoJSONEncoder)
                )
                return JsonResponse({
                    "success": True,
                    "data":"Login Successfully!"
                }, status=200) 
        else:
       
            return JsonResponse({
                "success": False,
                "data":"Invalid User!"
            }, status=200) 
        
        """
        if user_obj:
            username = user_obj.username
            user = authenticate(username=username , password=password)
            if user is None:
                return redirect('/signin/')
            else:
                return redirect('master/dashboard')
        else:
            return redirect('/signin/')
        """


class Signup(TemplateView):
    template_name = 'master/signup.html'
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        pass


class Dashboard(TemplateView):
    template_name = 'master/dashboard.html'
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())


class Sidebar(View):
    def get(self, request, *args, **kwargs):
        modules = kwargs.get('module')
        sidebarList =  Module.objects.filter(status=1).values()
       
        return JsonResponse({
            "success": True,
            "data":list(sidebarList)
        }, status=200) 

@RoleRequired('Permission')
class Permissions(TemplateView):
    template_name = 'master/permission.html'
    def get(self, request, *args, **kwargs):
        roleId = kwargs.get('role', '')
        if roleId and 'Edit' in kwargs.get('permission'):
            module = Module.objects.all()
            allow = '<ul class="list-group">'
            for m in module:
                  perm = Permission.objects.filter(modules_id=m.id,role_id=roleId).first()
                  if m.parent_id=='':
                        allow +=(f'<li class="list-group-item ">'
                                    f'<div class="w-100 d-flex justify-content-between">'
                                    f'<div>{m.module}</div>'
                                    f'<div>View <input type="checkbox" name="{m.module}" value="View" {"checked" if perm else None} class="form-check-input" /> </div>'
                                    f'</div>'
                                    f'{self.checkParent(roleId,module,m.id)}'
                                    f'</li>')   
            
            allow +='</ul>'
            self.template_name = 'master/allowpermission.html'
            return self.render_to_response(self.get_context_data(permissions=allow))
        else:
            return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
            data = json.loads(request.body)
            start = int(data.get('start', 1))
            length = int(data.get('length', 10))
            search = data.get('search', '')
            startIndex = (int(start)-1) * int(length)
            endIndex = startIndex + int(length)
            listData = []
            roles = kwargs.get('roleIds')
            if search :
                  data = Access.objects.filter(name__icontains=search,id__in=roles)[startIndex:endIndex].all()
                  totalLen = list(Access.objects.filter(name__icontains=search,id__in=roles).all())
            else:
                  data = Access.objects.filter(id__in=roles)[startIndex:endIndex].all()
                  totalLen = list(Access.objects.filter(id__in=roles).all())
            
            for i in data:

                  permission = {
                  "id":i.id,
                  "roleName":i.role.name,
                  "action":(f'<a class="btn btn-primary" href="{settings.BASE_URL}master/administration/permissions/{i.id}" >Permission</a>')
                  }
                  listData.append(permission)

            return JsonResponse({
                  "success": True,
                  "iTotalRecords":len(totalLen),
                  "iTotalDisplayRecords":len(totalLen),
                  "aaData":listData
            }, status=200)   
    
    def checkParent(self, role, module, mid):
        allow = '<ul class="list-group">'
        for m in module:
            perm = Permission.objects.filter(modules_id=m.id,role_id=role).first()
            if m.parent_id == str(mid):
                        checked = []
                        if perm:
                           checked = perm.permission.split(',')
                       
                        allow +=(f'<li class="list-group-item">'
                                    f'<div class="w-100 d-flex justify-content-between">'
                                    f'<div>{m.module}</div>'
                                    f'<div>View <input name="{m.module}[view]" type="checkbox" value="View" {"checked" if "View" in checked else None } class="form-check-input" />'
                                    f'Add <input name="{m.module}[add]" type="checkbox" value="Add" {"checked" if "Add" in checked else None }  class="form-check-input" />' 
                                    f'Edit <input name="{m.module}[edit]" type="checkbox" value="Edit" {"checked" if "Edit" in checked else None } class="form-check-input" />'
                                    f'Delete <input name="{m.module}[delete]" type="checkbox" value="Delete" {"checked" if "Delete" in checked else None } class="form-check-input" /></div>'
                                    f'</div>'
                                    f'{self.checkParent(role,module,m.id)}'
                                 f'</li>')   
                 
        allow +='</ul>'
      
        return allow

@RoleRequired('Module')
class ModuleList(TemplateView):
    template_name = 'master/module.html'

    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def put(self, request, *args, **kwargs):
            data = json.loads(request.body)
            parentId = kwargs.get('parentId', '')
            start = int(data.get('start', 1))
            length = int(data.get('length', 10))
            search = data.get('search', '')
            startIndex = (int(start)-1) * int(length)
            endIndex = startIndex + int(length)
            listData = []
            action =''
            if search :
                  data = Module.objects.filter(Q(parent_id=parentId),name__icontains=search)[startIndex:endIndex]
                  totalLen = Module.objects.filter(Q(parent_id=parentId),name__icontains=search).count()
            else:
                  data = Module.objects.filter(Q(parent_id=parentId))[startIndex:endIndex]
                  totalLen = Module.objects.filter(Q(parent_id=parentId)).count()
     
            for i in data:
                  action_btn = ''
                  if 'Edit' in kwargs.get('permission'):
                      if parentId:
                        action_btn += f'<a class="btn btn-primary" href="{settings.BASE_URL}movieplanet/admin/setting/module/{i.id}/{parentId}">Edit</a>' 
                      else:
                        action_btn += f'<a class="btn btn-primary" href="{settings.BASE_URL}movieplanet/admin/setting/module/{i.id}">Edit</a>'   
                  if 'Delete' in kwargs.get('permission'):
                      action_btn += f'<button class="btn btn-danger" onclick="deleteModal({i.id})">Delete</button>' 
                  if i.moduleType=="2":
                     link = (f'<a href="{settings.BASE_URL}master/administration/modules/{i.id}">{i.module}</a>')
                  else:
                      link = i.module
                  permission = {
                  "id":i.id,
                  "module":link,
                  "action":action_btn
                  }
                  listData.append(permission)
 
            return JsonResponse({
            "success": True,
            "iTotalRecords":totalLen,
            "iTotalDisplayRecords":totalLen,
            "aaData":listData,
            "action":action
            }, status=200)


@RoleRequired('User')
class Client(TemplateView):
    template_name = 'master/user.html'
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def put(self, request, *args, **kwargs):
            data = json.loads(request.body)
            start = int(data.get('start', 1))
            length = int(data.get('length', 10))
            search = data.get('search', '')
            startIndex = (int(start)-1) * int(length)
            endIndex = startIndex + int(length)
            listData = []
            totalLen=0
            
            cids = self.checkRoles(kwargs.get('authId'),kwargs.get('roleIds'),[kwargs.get('authId')])
            print(cids)     
            if search:
                  data = User.objects.filter(is_superuser="0",username__icontains=search).exclude(id__in=cids).filter(roles__role_id__in=kwargs.get('roleIds')).distinct()[startIndex:endIndex]
                  totalLen = User.objects.filter(is_superuser="0",username__icontains=search).exclude(id__in=cids).filter(roles__role_id__in=kwargs.get('roleIds')).distinct().count()
            else:
                  data = User.objects.filter(is_superuser="0",username__icontains=search).exclude(id__in=cids).filter(roles__role_id__in=kwargs.get('roleIds')).distinct()[startIndex:endIndex]
                  totalLen = User.objects.filter(is_superuser="0",username__icontains=search).exclude(id__in=cids).filter(roles__role_id__in=kwargs.get('roleIds')).distinct().count()

            for i in data:
                  btn =''
                  if 'Edit' in kwargs.get('permission'):
                        btn += f'<a class="btn btn-primary" href="{settings.BASE_URL}master/administration/user/{i.id}" >Edit</a>'
                  post = {
                        "id":i.id,
                        "name":i.username,
                        "email":i.email,
                        "action":btn
                  }
                  listData.append(post)
            
            return JsonResponse({
                        "success": True,
                        "iTotalRecords":totalLen,
                        "iTotalDisplayRecords":totalLen,
                        "aaData":listData
            }, status=200)

    def checkRoles(self, aid, rids, collected=None):
        if collected is None:
           collected = []
        if User.objects.filter(id=aid,is_superuser=1).exists():
           return collected
        data = User.objects.exclude(id=aid).all()
        gids = list(Access.objects.filter(user_id=aid).filter(
            ~Q(given_id=None)
        ).values('given_id', 'role_id').distinct())
        ids = list(set(map(lambda x: x['given_id'], gids)))

        for i in data:
            cgids = list(i.roles.filter(
            ~Q(given_id=None)
            ).values('given_id', 'role_id').distinct())
            
            if i.is_superuser == 1:
               collected.append(i.id) 
            elif all(item in cgids for item in gids):  
               collected.append(i.id) 
            elif i.id in ids and i.id not in collected:
               collected.append(i.id)
               self.checkRoles(i.id, rids, collected)
        return collected   

            
@RoleRequired('Post')
class Post(TemplateView):
    template_name = 'master/post.html'
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())


    def put(self, request, *args, **kwargs):
            parentId = kwargs.get('parentId', None)
            postId = kwargs.get('postId', None)
            action = {}
            data = json.loads(request.body.decode('utf-8'))
            start = int(data.get('start', 1))
            tickall = int(data.get('tickall', False))
            length = int(data.get('length', 10))
            search = data.get('search', '')
            startIndex = (int(start)-1) * int(length)
            endIndex = startIndex + int(length)
            item = data.get('item', [])
            status = data.get('status', '')
            trand = data.get('trand', '')
            # if status=="1" or status=="0":
            #    for i in item:
            #        if i['check']:
            #           Posts.objects.filter(id=i['id']).update(status=status)

            # if trand=="1" or trand=="0":
            #    for i in item:
            #        if i['check']:
            #           if trand == "1":
            #              if not Trand.objects.filter(post_id=i['id']).exists():
            #                   Trand.objects.create(
            #                   post_id=i['id'],
            #                   status=1
            #                   )
            #           elif trand == "0":
            #              Trand.objects.filter(post_id=i['id']).delete()
            
            if search :
                  data = Posts.objects.filter(Q(parent=parentId),name__icontains=search)[startIndex:endIndex].all()
                  totalLen = Posts.objects.filter(Q(parent=parentId),name__icontains=search).count()
            
            else:
                  data = Posts.objects.filter(Q(parent=parentId)).all()[startIndex:endIndex]
                  totalLen = Posts.objects.filter(Q(parent=parentId)).count()
            
            listData = []
            for i in data:
                  
                  btn =''
                  if 'Edit' in kwargs.get('permission'):
                     if parentId:
                        btn += f'<a class="btn btn-primary" href="{settings.BASE_URL}master/website/post/{i.id}/{parentId}" >Edit</a>'
                     else:
                        btn += f'<a class="btn btn-primary" href="{settings.BASE_URL}master/website/post/{i.id}" >Edit</a>'  
                  if 'Delete' in kwargs.get('permission'):
                     btn += f'<button class="btn btn-danger" onclick="deleteModal({i.id})">Delete</button>'
                  
                  link = i.name
                  if i.type==2:
                     link = f'<a href="{settings.BASE_URL}master/website/posts/{i.id}" >{i.name}</a>'
                  trow = ''
                #   trand = i.trands.first()
                #   if trand and trand.post_id == i.id:
                #      trow = '<span class="badge bg-primary">Trand</span>'
                #   else:
                #       trow = ''

                  post = {
                        "id":f'<div class="d-flex justify-content-between"><span>{i.id}</span> <input type="checkbox" {"checked" if tickall else ""} name="item[{i.id}]" value="{i.id}" class="item" /></div>',
                        "name":link,
                       
                        "trand":trow,
                        "rate":i.rate,
                        "status":(
                        '<span class="badge bg-success">Active</span>' if i.status == "1"
                        else '<span class="badge bg-danger">Deactive</span>'
                        ),
                        "action":btn
                  }
                        
                  listData.append(post)
            if 'Edit' in kwargs.get('permission'):
                action['status'] = """
                                    <div class="dropdown">
                                          <button class="btn border dropdown-toggle" type="button" id="dropdownMenu" data-bs-toggle="dropdown" aria-expanded="false">
                                            Status update
                                          </button>
                                          <ul class="dropdown-menu"  aria-labelledby="dropdownMenu">
                                                <li>
                                                      <select name="status" class="form-select me-2" id="status-update" >
                                                            <option value="">Status</option>
                                                            <option value="1">Active</option>
                                                            <option value="0">Deactive</option>
                                                      </select>    
                                                </li>
                                                <li>
                                                      <select name="trand" class="form-select me-2" id="trand-update" >
                                                            <option value="">Trand</option>
                                                            <option value="1">Active</option>
                                                            <option value="0">Deactive</option>
                                                      </select>  
                                                </li>
                                                
                                          </ul>
                                    </div>
                                                                  
                                   """


            return JsonResponse({
                  "success": True,
                  "iTotalRecords":totalLen,
                  "iTotalDisplayRecords":totalLen,
                  "aaData":listData,
                  "action":action
            }, status=200)

   
@RoleRequired('Menu')
class Menus(TemplateView):
    template_name = 'master/menu.html'
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
            data = json.loads(request.body)
            parentId = kwargs.get('parentId', None)
            start = int(data.get('start', 1))
            length = int(data.get('length', 10))
            search = data.get('search', '')
            startIndex = (int(start)-1) * int(length)
            endIndex = startIndex + int(length)
            listData = []
            action=''
            if search:
                  data = Menu.objects.filter(Q(menuId=parentId),name__icontains=search)[startIndex:endIndex]
                  totalLen = Menu.objects.filter(Q(menuId=parentId),name__icontains=search).count()
            else:
                  data = Menu.objects.filter(Q(menuId=parentId))[startIndex:endIndex]
                  totalLen = Menu.objects.filter(Q(menuId=parentId)).count()

    
            for i in data:
                  action_btn = ''
                  if 'Edit' in kwargs.get('permission'):
                      if parentId:
                        action_btn += f'<a class="btn btn-primary" href="{settings.BASE_URL}movieplanet/admin/website/menu/{i.id}/{parentId}">Edit</a>' 
                      else:
                        action_btn += f'<a class="btn btn-primary" href="{settings.BASE_URL}movieplanet/admin/website/menu/{i.id}">Edit</a>'   
                  if 'Delete' in kwargs.get('permission'):
                      action_btn += f'<button class="btn btn-danger" onclick="deleteModal({i.id})">Delete</button>' 
                  if i.type==2:
                     link = (f'<a href="{settings.BASE_URL}master/website/menus/{i.id}">{i.name}</a>')
                  else:
                      link = i.name
                  permission = {
                  "id":i.id,
                  "name":link,
                  "action":action_btn
                  }
                  listData.append(permission)
 
            return JsonResponse({
            "success": True,
            "iTotalRecords":totalLen,
            "iTotalDisplayRecords":totalLen,
            "aaData":listData,
            "action":action
            }, status=200)

class Modules(TemplateView):
    template_name = 'master/module.html'
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        pass


