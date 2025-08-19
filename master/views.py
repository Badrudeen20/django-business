from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.shortcuts import render,redirect
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User 
from django.db.models import OuterRef,Exists
from django.views import View
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from .forms import RegisterForm, LoginForm, MenuForm, PostForm
from django.contrib import messages
from master.models import *
from user.models import *
from django.conf import settings
import pandas as pd
import json
from master.decorators import (
   RoleRequired
)

class Signin(TemplateView):
    template_name = 'master/signin.html'
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data["user"]
            login(request, user)
            request.session['master'] = json.loads(
                json.dumps({
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'is_admin':user.is_superuser
                }, cls=DjangoJSONEncoder)
            )
        return self.render_to_response(self.get_context_data(form=form))

        
        """

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
        form = RegisterForm(request.POST)

        if form.is_valid():
           
            try:
                # user = User.objects.create_user(
                #     username=form.cleaned_data["username"],
                #     email=form.cleaned_data["email"],
                #     password=form.cleaned_data["password"]
                # )
                # login(request, user)
                form.save()
                messages.success(request, "Account created successfully! Please log in.")
                return redirect('master:signin')
            except Exception as e:
                messages.error(request, e)
                return HttpResponseRedirect(reverse('master:signup'))
        else:
            messages.error(request, "Please correct the errors below.")   
        return self.render_to_response(self.get_context_data(form=form))


class Logout(View):
    def get(self, request):
        logout(request)
        request.session.flush()
        return HttpResponseRedirect(reverse('master:signin'))


class Dashboard(TemplateView):
    template_name = 'master/dashboard.html'
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())


@RoleRequired(None)
class Sidebar(View):
    def get(self, request, *args, **kwargs):
        modules = kwargs.get('module')
        sidebarList =  Module.objects.filter(module__in=modules,status=1).values()
       
        return JsonResponse({
            "success": True,
            "data":list(sidebarList)
        }, status=200) 


@RoleRequired('Permission')
class Permissions(TemplateView):
    
    def __init__(self, *args, **kwargs):
        self.template_name = 'master/permission.html'
        super().__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if 'View' not in kwargs.get('permission'):
           self.template_name = 'master/401.html'  
        return super().dispatch(request, *args, **kwargs)

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

    def put(self, request, *args, **kwargs):
            data = json.loads(request.body)
            start = int(data.get('start', 1))
            length = int(data.get('length', 10))
            search = data.get('search', '')
            startIndex = (int(start)-1) * int(length)
            endIndex = startIndex + int(length)
            listData = []
            roles = kwargs.get('roleIds')
            if search :
                  data = Role.objects.filter(name__icontains=search,id__in=roles)[startIndex:endIndex].all()
                  totalLen = list(Role.objects.filter(name__icontains=search,id__in=roles).all())
            else:
                  data = Role.objects.filter(id__in=roles)[startIndex:endIndex].all()
                  totalLen = list(Role.objects.filter(id__in=roles).all())
            
            for i in data:
                  permission = {
                  "id":i.id,
                  "roleName":i.name,
                  "action":(f'<a class="btn btn-primary" href="{settings.BASE_URL}master/administration/permission/{i.id}" >Permission</a>')
                  }
                  listData.append(permission)

            return JsonResponse({
                  "success": True,
                  "iTotalRecords":len(totalLen),
                  "iTotalDisplayRecords":len(totalLen),
                  "aaData":listData
            }, status=200)   
    
    def post(self, request, *args, **kwargs):
            roleId = kwargs.get('role', '')
            if roleId and 'Edit' in kwargs.get('permission'):
                module = Module.objects.all()
                for m in module:
                    perm = Permission.objects.filter(modules_id=m.id,role_id=roleId).first()
                    if m.parent_id=='':
                        if perm:
                            if m.module in request.POST:
                               perm.permission =  request.POST[m.module]
                               perm.save()
                            else:
                               perm.delete()
                        else:
                            if m.module in request.POST:
                                Permission.objects.create(
                                permission=request.POST[m.module],
                                role_id = roleId,
                                modules_id = m.id
                                )
                    else:
                        if m.parent_id:
                              permission = ''
                              if m.module+'[view]' in request.POST:
                                    permission += request.POST[m.module+'[view]']
                              if m.module+'[add]' in request.POST:
                                    permission +=','+request.POST[m.module+'[add]']
                              if m.module+'[edit]' in request.POST:
                                    permission +=','+request.POST[m.module+'[edit]']
                              if m.module+'[delete]' in request.POST:
                                    permission +=','+request.POST[m.module+'[delete]']
                                       
                              if perm:
                                if permission:
                                    perm.permission =  permission
                                    perm.save()
                                else:
                                    perm.delete()  
                              else:
                                  if permission:
                                    Permission.objects.create(
                                        permission=permission,
                                        role_id = roleId,
                                        modules_id = m.id,
                                        module_parent_id=m.parent_id
                                    )
                                   
                return HttpResponseRedirect(reverse('master:permission', args=[roleId]))       
            return redirect(reverse('master:permissions'))
    
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
class Modules(TemplateView):

    def __init__(self, *args, **kwargs):
        self.template_name = 'master/module.html'
        super().__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if 'View' not in kwargs.get('permission'):
           self.template_name = 'master/401.html'  
        return super().dispatch(request, *args, **kwargs)

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

    def __init__(self, *args, **kwargs):
        self.template_name = 'master/user.html'
        super().__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if 'View' not in kwargs.get('permission'):
           self.template_name = 'master/401.html'  
        return super().dispatch(request, *args, **kwargs) 

    def get(self, request, *args, **kwargs):
        userId = kwargs.get('userId', None)
        if userId and 'Edit' in kwargs.get('permission'):
            clientIds = self.clients(kwargs.get('authId'),kwargs.get('isAdmin'))
            if userId in clientIds or User.objects.filter(access__isnull=True,id=userId).exists():
               self.template_name = 'master/useredit.html'
               roles = Access.objects.filter(user_id=kwargs.get('authId')).annotate(
                       checked=Exists(Access.objects.filter(user_id=userId,role_id=OuterRef('role_id')))
                       ).all()
               return self.render_to_response(self.get_context_data(roles=roles))
            else:
               return HttpResponseRedirect(reverse('master:users'))
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
            clientIds = self.clients(kwargs.get('authId'),kwargs.get('isAdmin'))

            if search:
                  data = User.objects.filter(Q(access__isnull=True) | Q(id__in=clientIds),is_superuser="0",username__icontains=search)[startIndex:endIndex]
                  totalLen = User.objects.filter(Q(access__isnull=True) | Q(id__in=clientIds),is_superuser="0",username__icontains=search).count()
            else:
                  data = User.objects.filter(Q(access__isnull=True) | Q(id__in=clientIds),is_superuser="0")[startIndex:endIndex]
                  totalLen = User.objects.filter(Q(access__isnull=True) | Q(id__in=clientIds),is_superuser="0").count()

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

    
    def post(self, request, *args, **kwargs):
        userId = kwargs.get('userId', None)
        if userId and 'Edit' in kwargs.get('permission'):
           
            clientIds = self.clients(kwargs.get('authId'),kwargs.get('isAdmin'))
            if userId in clientIds or User.objects.filter(access__isnull=True,id=userId).exists():
               roles = Access.objects.filter(user_id=kwargs.get('authId')).all()
               for r in roles:
                   if r.role.name in request.POST:
                      if Access.objects.filter(user_id=userId,role_id=r.id).exists():
                         role = Access.objects.filter(user_id=userId,role_id=r.id).first()
                         role.given_id = kwargs.get('authId')
                         role.save()
                      else:
                         Access.objects.create(
                         user_id = userId,
                         role_id = r.id,
                         given_id = kwargs.get('authId')
                         )
                   elif Access.objects.filter(user_id=userId,role_id=r.id).exists():
                        Access.objects.filter(user_id=userId,role_id=r.id).delete()
               return HttpResponseRedirect(reverse('master:user', args=[userId])) 
            else:
                return HttpResponseRedirect(reverse('master:users')) 
    def clients(self, authId,isAdmin):
        if isAdmin:
           return list(Access.objects.exclude(user_id=authId).distinct().values_list('user_id', flat=True))
        else:
           return list(Access.objects.filter(given_id=authId).values_list('user_id', flat=True))


@RoleRequired('Posts')
class Post(TemplateView):
    template_name = 'master/post.html'

    def __init__(self, *args, **kwargs):
        self.template_name = 'master/post.html'
        super().__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if 'View' not in kwargs.get('permission'):
           self.template_name = 'master/401.html'  
        return super().dispatch(request, *args, **kwargs) 


    def get(self, request, *args, **kwargs):
        parentId = kwargs.get('parentId', None)
        postId = kwargs.get('postId', None)
        action = {}
        if 'Add' in kwargs.get('permission'):
            if parentId:
                action['add'] = f'<a class="btn btn-primary" href="{settings.BASE_URL}master/website/post/create/{parentId}">Add</a>'
            else:
                action['add'] = f'<a class="btn btn-primary" href="{settings.BASE_URL}master/website/post/create">Add</a>'
                action['excel'] = f'<a class="btn btn-info" href="{settings.BASE_URL}master/website/excel">Excel</a>'
            if postId=='create':
               self.template_name = "master/postedit.html"
               if parentId and not Posts.objects.filter(id=parentId,type=2).exists():
                  return HttpResponseRedirect(reverse('master:posts', args=[parentId]))
               return self.render_to_response(self.get_context_data())    
              
            if postId and 'Edit' in kwargs.get('permission'):
               post = Posts.objects.filter(Q(parent=parentId),id=postId).values().first()
               if post:
                  self.template_name = "master/postedit.html"
                  return self.render_to_response(self.get_context_data(post=post))
               return HttpResponseRedirect(reverse('master:posts')) 
    

        return self.render_to_response(self.get_context_data(action=action))

    def post(self, request, *args, **kwargs):
        form = PostForm(request.POST)
        parentId = kwargs.get('parentId', None)
        postId = kwargs.get('postId', None)
        if form.is_valid():
            if postId=='create' and 'Add' in kwargs.get('permission'):
                    post = request.POST
                    links = []
                    obj = {}
                    for key, value in request.POST.items(): 
                        if key.startswith("link[") and key.endswith("][url]"):
                            obj['url'] = value
                            
                        if key.startswith("link[") and key.endswith("][download]"):
                            obj['download'] = value

                        if 'url' in obj and 'download' in obj:
                           links.append(obj)
                           obj = {}
                    
                    Posts.objects.create(
                        name=post.get('name', ''),
                        image=post.get('image', ''),
                        rate=post.get('rate', ''),
                        size=post.get('size', ''),
                        genre=post.get('genre', ''),
                        lang=post.get('lang', ''),
                        status=post.get('status', ''),
                        starcast=post.get('starcast', ''),
                        story=post.get('story', ''),
                        link=links,
                        menu=post.get('menu', ''),
                        parent=parentId,
                        duration=post.get('duration', ''),
                        release_date=post.get('release_date', '')
                    )
                    return HttpResponseRedirect(reverse('master:posts')) 
            elif int(postId) and 'Edit' in kwargs.get('permission'):
                    post = request.POST
                    links = []
                    obj = {}
                    for key, value in request.POST.items(): 
                        if key.startswith("link[") and key.endswith("][url]"):
                            obj['url'] = value
                            
                        if key.startswith("link[") and key.endswith("][download]"):
                            obj['download'] = value

                        if 'url' in obj and 'download' in obj:
                           links.append(obj)
                           obj = {}

                    if parentId:
                        update = Posts.objects.filter(parent=parentId,id=postId).first()
                    else:
                        update = Posts.objects.filter(id=postId).first()
                    if update:
                        update.image = post.get('image', '')
                        update.rate = post.get('rate', '')
                        update.size = post.get('size', '')
                        update.genre = post.get('genre', '')
                        update.lang = post.get('lang', '')
                        update.status = post.get('status', '')
                        update.starcast = post.get('starcast', '')
                        update.story = post.get('story', '')
                        update.link = links
                        update.menu = post.get('menu', '')
                        update.duration=post.get('duration', '')
                        update.release_date = post.get('release_date', '')
                        update.save()
                        if parentId:
                            return HttpResponseRedirect(reverse('master:post', args=[postId, parentId]))
                        return HttpResponseRedirect(reverse('master:post', args=[postId]))
            return HttpResponseRedirect(reverse('master:posts'))   
        else:
            self.template_name = 'master/postedit.html'
            return self.render_to_response(self.get_context_data(form=form))

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
            
            if status=="1" or status=="0":
               for i in item:
                   if i['check']:
                      Posts.objects.filter(id=i['id']).update(status=status)

            if trand=="1" or trand=="0":
               for i in item:
                   if i['check']:
                      Posts.objects.filter(id=i['id']).update(trand=trand)

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
    
                  if i.trand:
                     trow = '<span class="badge bg-primary">Trand</span>'
                  else:
                      trow = ''

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

    def patch(self, request, *args, **kwargs):
        if 'Delete' in kwargs.get('permission'):
            data = json.loads(request.body)
            Posts.objects.filter(id=data.get('id')).delete()
            Posts.objects.filter(parent=data.get('id')).delete()
            return JsonResponse({
                    "status": True,
                    "msg":"Item delete successfully!"
            }, status=200)


@RoleRequired('Posts')
class Excel(TemplateView):

    def __init__(self, *args, **kwargs):
        self.template_name = 'master/excel.html'
        super().__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if 'View' not in kwargs.get('permission'):
           self.template_name = 'master/401.html'  
        return super().dispatch(request, *args, **kwargs) 


    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())
    
    def post(self, request, *args, **kwargs):
        if 'Edit' in kwargs.get('permission') and 'Add' in kwargs.get('permission'):
            file = request.FILES['files']
            df = pd.read_excel(file)
            data_array = df.to_dict(orient="records")
            for row in data_array:  
                if Posts.objects.filter(name=row.get('name', '')).exists():
                    update = Posts.objects.filter(name=row.get('name', '')).first()
                    if update:
                        update.image = row.get('image', '')
                        update.rate = row.get('rate', '')
                        update.size = row.get('size', '')
                        update.genre = row.get('genre', '')
                        update.lang = row.get('lang', '')
                        update.status = row.get('status', '')
                        update.starcast = row.get('starcast', '')
                        update.story = row.get('story', '')
                        update.menu = row.get('menu', '')
                        update.duration=row.get('duration', '')
                        update.release_date = row.get('release_date', None)
                        update.save()
                else:
                    Posts.objects.create(
                        name=row.get('name', ''),
                        image=row.get('image', ''),
                        rate=row.get('rate', ''),
                        size=row.get('size', ''),
                        genre=row.get('genre', ''),
                        lang=row.get('lang', ''),
                        status=row.get('status', ''),
                        starcast=row.get('starcast', ''),
                        story=row.get('story', ''),
                        menu=row.get('menu', ''),
                        duration=row.get('duration', ''),
                        release_date=row.get('release_date', None)
                    )
            return HttpResponseRedirect(reverse('master:excel')) 
        

@RoleRequired('Menu')
class Menus(TemplateView):

    def __init__(self, *args, **kwargs):
        self.template_name = 'master/menu.html'
        super().__init__(*args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        if 'View' not in kwargs.get('permission'):
           self.template_name = 'master/401.html'  
        return super().dispatch(request, *args, **kwargs) 
        
    def get(self, request, *args, **kwargs):
        parentId = kwargs.get('parentId', None)
        menuId = kwargs.get('menuId', None)
        action = {}

        if 'Add' in kwargs.get('permission'):
            if parentId:
                action['add'] = f'<a class="btn btn-primary" href="{settings.BASE_URL}master/website/menu/create/{parentId}">Add</a>'
            else:
                action['add'] = f'<a class="btn btn-primary" href="{settings.BASE_URL}master/website/menu/create">Add</a>'
        
            if menuId=='create':
                if parentId and not Menu.objects.filter(id=parentId,type=2).exists():
                    return HttpResponseRedirect(reverse('master:menus')) 
                else:
                    self.template_name = "master/menuedit.html" 
                    return self.render_to_response(self.get_context_data())
                    
        if menuId and 'Edit' in kwargs.get('permission'):
            if parentId:
                menu = Menu.objects.filter(id=menuId,menuId=parentId).values().first()
            else:
                menu = Menu.objects.filter(id=menuId).values().first()
            if menu:
                self.template_name = "master/menuedit.html"
                return self.render_to_response(self.get_context_data(menu=menu))

            return HttpResponseRedirect(reverse('master:menus')) 

        return self.render_to_response(self.get_context_data(action=action))

    def post(self, request, *args, **kwargs):
        form = MenuForm(request.POST)
        parentId = kwargs.get('parentId', None)
        menuId = kwargs.get('menuId', None)
        
        if form.is_valid():
            if menuId =='create' and 'Add' in kwargs.get('permission'):
                    Menu.objects.create(
                    name=request.POST['menu'], 
                    link=request.POST['link'],
                    type=request.POST['type'],
                    menuId=parentId,
                    status=1
                    )
                    return HttpResponseRedirect(reverse('master:menus')) 
            elif int(menuId) and 'Edit' in kwargs.get('permission'):
                    if parentId:
                        update = Menu.objects.filter(menuId=parentId,id=menuId).first()
                    else:
                        update = Menu.objects.filter(id=menuId).first()
                    if update:
                        update.name = request.POST['menu']
                        update.link = request.POST['link']
                        update.save()
                        if parentId:
                            return HttpResponseRedirect(reverse('master:menu', args=[menuId, parentId]))
                        return HttpResponseRedirect(reverse('master:menu', args=[menuId]))
            return HttpResponseRedirect(reverse('master:menus'))  
        else:
            self.template_name = 'master/menuedit.html'
            return self.render_to_response(self.get_context_data(form=form))
        
   
    def put(self, request, *args, **kwargs):
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
                        action_btn += f'<a class="btn btn-primary" href="{settings.BASE_URL}master/website/menu/{i.id}/{parentId}">Edit</a>' 
                      else:
                        action_btn += f'<a class="btn btn-primary" href="{settings.BASE_URL}master/website/menu/{i.id}">Edit</a>'   
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

    def patch(self, request, *args, **kwargs):
        if 'Delete' in kwargs.get('permission'):
            data = json.loads(request.body)
            Menu.objects.filter(id=data.get('id')).delete()
            Menu.objects.filter(menuId=data.get('id')).delete()
            
            return JsonResponse({
                    "status": True,
                    "msg":"Item delete successfully!"
            }, status=200)

