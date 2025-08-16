from django.views.generic.edit import CreateView
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from django.shortcuts import render
from datetime import datetime
from django.db.models import Q
from user.models import *
import json


class Home(TemplateView):

    template_name = 'user/home.html'
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        
        start = data.get('start')
        length = data.get('length')
        search = data.get('search')
        startIndex = (int(start)-1) * int(length)
        endIndex = startIndex + int(length)
        Link = kwargs.get('Link', None)
        
        rates = request.GET.get('rates', '')
        min_rate, max_rate = rates.split(',') if rates else (0, 10)

        years = request.GET.get('years', '')
        start_year, end_year = years.split(',') if years else (1900, datetime.now().year)
        
        genre = request.GET.get('genres', '')
        genres = genre.split(',') if genre else []

        query = Q()
        for word in genres:
            query |= Q(genre__icontains=word)
        
        if Link:
                linkList = Link.split("+")
                Link = " ".join(linkList)
                parent = Posts.objects.filter(name=Link,status=1).first()
                Link = parent.id
        if search:
            data = Posts.objects.filter(query,Q(parent=Link),Q(release_date__year__gte=start_year),Q(release_date__year__lte=end_year),rate__range=(min_rate, max_rate),name__icontains=search,status=1)[startIndex:endIndex]
            totalLen = Posts.objects.filter(query,Q(parent=Link),Q(release_date__year__gte=start_year),Q(release_date__year__lte=end_year),rate__range=(min_rate, max_rate),name__icontains=search,status=1).count()
        
        else:
            data = Posts.objects.filter(query,Q(parent=Link),Q(release_date__year__gte=start_year),Q(release_date__year__lte=end_year),rate__range=(min_rate, max_rate),status=1)[startIndex:endIndex]
            totalLen = Posts.objects.filter(query,Q(parent=Link),Q(release_date__year__gte=start_year),Q(release_date__year__lte=end_year),rate__range=(min_rate, max_rate),status=1).count()
           
        listData = []
        for i in data:
                post = {
                    "id":i.id,
                    "name":i.name,
                    "image":i.image,
                    "rate":i.rate,
                    "type":i.type
                }     
                listData.append(post)
        
        return JsonResponse({
        "success": True,
        "iTotalRecords":totalLen,
        "iTotalDisplayRecords":totalLen,
        "aaData":listData
        }, status=200)
        

   
class Login(TemplateView):

    template_name = 'user/login.html'
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        return JsonResponse({'message': 'POST received', 'data': data})


class Register(TemplateView):

    template_name = 'user/register.html'
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        return JsonResponse({'message': 'POST received', 'data': data})
    
class Category(TemplateView):
    template_name = 'user/home.html'
    def get(self, request, *args, **kwargs):
        return self.render_to_response(self.get_context_data())

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        start = data.get('start')
        length = data.get('length')
        search = data.get('search')
        startIndex = (int(start)-1) * int(length)
        endIndex = startIndex + int(length)
        params  = kwargs.get('params')
        categories = params.replace("/", " ").split()
        query = Q()

        for word in categories:
            query &= Q(menu__icontains=word)
        if search :
                data = Posts.objects.filter(query,parent=None,name__icontains=search,status=1)[startIndex:endIndex].all()
                totalLen = Posts.objects.filter(query,parent=None,name__icontains=search,status=1).count()
        
        else:
                data = Posts.objects.filter(query,parent=None,status=1)[startIndex:endIndex].all()
                totalLen = Posts.objects.filter(query,parent=None,status=1).count()
        
        listData = []
        for i in data:
                post = {
                    "id":i.id,
                    "name":i.name,
                    "image":i.image,
                    "rate":i.rate,
                    "type":i.type
                }     
                listData.append(post)
        
        return JsonResponse({
        "success": True,
        "iTotalRecords":totalLen,
        "iTotalDisplayRecords":totalLen,
        "aaData":listData
        }, status=200)      
        
    
class Menubar(View):

    def get(self, request, *args, **kwargs):
        try:
            menu = Menu.objects.filter(status=1).all()
            html = ''
            for m in menu:
                if m.menuId is None:
                   if m.type == 2:
                        html += (f'<li><button class="nav-link dropdown-btn" data-dropdown="dropdown{m.id}" aria-haspopup="true" aria-expanded="false" aria-label="discover">{m.name}<i class="bx bx-chevron-down" aria-hidden="true"></i></button>'
                                    f'{self.menuBarLoop(menu,m.id)}'
                                    f'</li>')
                   elif m.type == 1:  
                        html += (f'<li><a class="nav-link dropdown-link dropdown-btn" data-dropdown="dropdown{m.id}" href="{ settings.BASE_URL }{m.link}" aria-haspopup="true" aria-expanded="false">{m.name}</a></li>')
                  
            return JsonResponse({"status":True,"Menus":html})
        except Exception as e:
            return JsonResponse({"status":False,"error": str(e)}, status=500)

    def menuBarLoop(self,Menus=[],MenuId=None,IsLoop=None):
            check = False
            menu = f'<div id="dropdown{MenuId}" class="dropdown"><ul role="menu">'
            arrow = ''
            if IsLoop:
                menu = f'<div id="dropdown{MenuId}" class="dropdown loopMenu"><ul role="menu">'
                arrow = '<i class="bx bx-chevron-down" aria-hidden="true"></i>'
            for m in Menus:
                check = True
                if m.menuId and int(m.menuId) == int(MenuId):
                        if m.type == 2:
                            menu += (f'<li><button class="nav-link dropdown-btn" data-dropdown="dropdown{m.id}" aria-haspopup="true" aria-expanded="false" aria-label="discover">{m.name}<i class="bx bx-chevron-down" aria-hidden="true"></i></button>'
                                        f'{self.menuBarLoop(menu,m.id)}'
                                        f'</li>')
                        elif m.type == 1:  
                            menu += (f'<li><a class="nav-link dropdown-link dropdown-btn" data-dropdown="dropdown{m.id}" href="{ settings.BASE_URL }{m.link}" aria-haspopup="true" aria-expanded="false">{m.name}</a></li>')
                                            
            menu +='</ul></div>'
            if check:
                return menu
            else:    
                return ''

            
class Detail(TemplateView):
      template_name = 'user/detail.html'
      def get(self, request, *args, **kwargs):
        Link = kwargs.get('Link', None)
        linkList = Link.split("+")
        MovieName = " ".join(linkList)
        data = Posts.objects.filter(name=MovieName,status=1).values().first()
        return self.render_to_response(self.get_context_data(link=Link,post=data))
      
      def put(self, request, *args, **kwargs):
        Link = kwargs.get('Link', None)
        return JsonResponse({"status":True,"Menus":Link})
      
