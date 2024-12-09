# home/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('post_flow', views.post_flow, name='post_flow'),
    path('start_interface', views.start_interface, name='start_interface'),
    path('get_data', views.get_data, name='get_data'),
    path('clear_db', views.clear_db, name='clear_db'),
    path('stop_interface', views.stop_interface, name='stop_interface'),
]