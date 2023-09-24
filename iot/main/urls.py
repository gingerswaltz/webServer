from django.urls import path
from . import views
from .views import Reading
from .views import ReadingCreateView, ReadingUpdateView, ReadingDeleteView, ReadingListView


urlpatterns = [
    path('', views.index, name='home' ),
    path('about', views.about, name='about'),
    path('graphics', views.graphics, name='graphics'),
    path('reading', ReadingListView.as_view, name='reading'),
    path('create/', ReadingCreateView.as_view(), name='reading_create'),
    path('/<int:pk>/update/', ReadingUpdateView.as_view(), name='reading_update'),
    path('/<int:pk>/delete/', ReadingDeleteView.as_view(), name='reading_delete'),
]


