from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('overview/', views.overview, name='overview'),
    path('search/', views.search, name='search'),
    #path('overview/<str:SpotifyID>', views.overview, name='overview'),
]