from django.urls import include, path
from . import views
# from .views import Reading
from .views import *
from django.contrib.auth import views as auth_views
urlpatterns = [
    path('', DashboardView.as_view(), name='home'),
    path('get-characteristics-data/<int:panel_id>/', views.get_characteristics_data_by_panel,
         name='get-characteristics-data-by-panel'),  # сводка по конкретной панели
       path('get_characteristics_by_date/<int:panel_id>/<str:selected_date>/', views.get_characteristics_by_date, name='get_characteristics_by_date'),
  # сводка по конкретной панели и дате
    path('get-general-characteristics-data/', get_general_characteristics_data,
         name='get-general-characteristics-data'),  # сводка общая
    path('socket/', views.socket, name='socket'), # устарело
    path('table/', CharTableView.as_view(), name='table'),
    path('panels/', views.solar_panels, name='panels'),
    path('characteristics-data/', characteristics_data,
         name='characteristics-data'),
    path('get_clients/', views.get_connected_clients, name='get_clients'),
    path('set_active_client/', views.set_active_client, name='set_active_client'),
    path('send_message/', views.send_message_to_client, name='send_message'),
    path('panels/panel_detail', views.panel_detail, name='panel_detail'),
    path('get_recent_char/<int:panel_id>/', views.get_recent_char, name='get_recent_char'),
    path('get_weather/', views.get_weather, name='get_weather'),
    path('update_client_status/', views.update_client_status, name='update_client_status'),
    # другие маршруты...
]
