from django.urls import path
from . import views
# from .views import Reading
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', DashboardView.as_view(), name='home' ),
    path('socket/', views.socket, name='socket'),
    path('get-characteristics-data/<int:installation_number>', views.get_characteristics_data, name='get-characteristics-data'),
    path('table/', CharTableView.as_view(), name='table' ),
    path('panels/', views.solar_panels, name='panels'),
    path('characteristics-data/', characteristics_data, name='characteristics-data'),
    path('get_clients/', views.get_connected_clients, name='get_clients'),
    path('set_active_client/', views.set_active_client, name='set_active_client'),
    path('send_message/', views.send_message_to_client, name='send_message'),
]


