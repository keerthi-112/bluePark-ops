from django.urls import path

from . import views

urlpatterns = [
    path('login',views.login, name='login'),
    path('',views.logout,name='logout'),
    path('register',views.register, name='register'),
    path('update', views.update, name='update'),
]