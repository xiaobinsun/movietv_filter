from django.urls import path
from django.conf import settings
from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('statis/', views.StatisPageView.as_view(), name='statis'),
    path('statis/hottest/', views.hottest, name='hottest'),
    path('statis/celebrity/', views.celebrity, name='celebrity'),
    path('filter/', views.filter, name='filter'),
]
