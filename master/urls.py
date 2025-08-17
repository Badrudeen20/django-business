from django.urls import path
# from . import views
from .views import Dashboard,Modules,Client,Permissions,Sidebar,Post,Menus,Signin,Signup,Logout


app_name = 'master'
urlpatterns=[
  path('dashboard/', Dashboard.as_view(),name="dashboard"),
  path('signin/', Signin.as_view(),name="signin"),
  path('signout/', Logout.as_view(),name='signout'),
  path('signup/', Signup.as_view(),name="signup"),

  path('administration/module/', Modules.as_view(),name="module"),
  path('administration/modules/<str:parentId>',Modules.as_view()),


  path('administration/permissions/', Permissions.as_view(),name="permissions"),
  path('administration/permission/<int:role>',Permissions.as_view(),name="permission"),

  path('website/posts/', Post.as_view(),name="post"),
  path('website/posts/<str:parentId>',Post.as_view(),name="posts"),
  path('website/post/<str:postId>',Post.as_view(),name="post"),
  path('website/post/<str:postId>/<str:parentId>',Post.as_view(),name="post"),


  path('website/menus/', Menus.as_view(),name="menus"),
  path('website/menus/<int:parentId>',Menus.as_view(),name="menus"),
  path('website/menu/<str:menuId>',Menus.as_view(),name="menu"),
  path('website/menu/<str:menuId>/<str:parentId>',Menus.as_view(),name="menu"),

  path('administration/users',Client.as_view(),name="users"),
  path('sidebar/', Sidebar.as_view(),name="sidebar"),
  
]