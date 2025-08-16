from django.urls import path
# from . import views
from .views import Dashboard,ModuleList,Client,Permissions,Sidebar,Post,Menus,Signin,Signup


app_name = 'master'
urlpatterns=[
  path('dashboard/', Dashboard.as_view(),name="dashboard"),
  path('signin/', Signin.as_view(),name="signin"),
  # path('signup/', Signup.as_view(),name="signup"),

  path('administration/module/', ModuleList.as_view(),name="module"),
  path('administration/modules/<str:parentId>',ModuleList.as_view()),
  path('administration/users/', Client.as_view(),name="user"),
  path('administration/permissions/', Permissions.as_view(),name="permission"),
  path('administration/permissions/<int:role>',Permissions.as_view()),
  path('website/posts/', Post.as_view(),name="post"),
  path('website/posts/<str:parentId>',Post.as_view(),name="posts"),
  path('website/menus/', Menus.as_view(),name="menu"),
  path('website/menus/<int:parentId>',Menus.as_view()),
  path('administration/users',Client.as_view(),name="users"),
  path('sidebar/', Sidebar.as_view(),name="sidebar"),
  
]