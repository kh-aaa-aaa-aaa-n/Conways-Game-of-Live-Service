from django.urls import path
from . import views

app_name = 'game' 

urlpatterns = [
    path('', views.start_page_view, name='start_page'),
    path('game/', views.game_view, name='game'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
]