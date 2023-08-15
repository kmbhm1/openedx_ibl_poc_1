from django.urls import path

from profiles import views

urlpatterns = [
    path('', views.login, name='index'),
    path('authorize/', views.authorize),
    path('greeting/', views.greeting, name='greeting'),
]
