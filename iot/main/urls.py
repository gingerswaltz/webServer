from django.urls import path
from . import views
# from .views import Reading
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', Dashboard.as_view(), name='home' ),
    path('socket/', views.socket, name='socket'),
    path('get-characteristics-data/<int:installation_number>', views.get_characteristics_data, name='get-characteristics-data'),
    path('table/', views.char_table, name='table' ),
    path('panels/', views.solar_panels, name='panels'),
    path('characteristics-data/', characteristics_data, name='characteristics-data'),
    path('panels/<int:pk>/', views.panel_detail, name='panel_detail'),
]


