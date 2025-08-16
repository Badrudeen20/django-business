from django.urls import path
#now import the views.py file into this code
# from . import views
from .views import Home,Login,Menubar,Detail,Category,Register

app_name = 'user'
urlpatterns=[
  path('',Home.as_view(),name="home"),
  path('login/',Login.as_view(),name="login"),
  path('register/',Register.as_view(),name="register"),
  path('menubar',Menubar.as_view(),name="menubar"),
  path('detail/<str:Link>/',Detail.as_view(),name="detail"),
  path('category/<path:params>/', Category.as_view()),
  path('<str:Link>',Home.as_view())
]