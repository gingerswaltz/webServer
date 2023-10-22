from django.urls import path
from . import views
# from .views import Reading
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.dashboard_char_table, name='home' ),
    path('table/', views.char_table, name='table' ),
    path('panels/', views.solar_panels, name='panels'),
]


