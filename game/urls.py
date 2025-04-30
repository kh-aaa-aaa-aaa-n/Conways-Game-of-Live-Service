
from django.urls import path
from . import views

from .views import CustomPasswordChangeView, CustomPasswordChangeDoneView

app_name = 'game'

urlpatterns = [
    # Existing URLs
    path('', views.start_page_view, name='start_page'),
    path('game/', views.game_view, name='game'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('learn-more/', views.learn_more, name='learn_more'),

    # Account Management URLs
    path('account/', views.account_view, name='account'),
    path('account/edit/', views.edit_account_view, name='edit_account'),
    path('account/password/', CustomPasswordChangeView.as_view(), name='password_change'),
    path('account/password/done/', CustomPasswordChangeDoneView.as_view(), name='password_change_done'),
    path('account/delete/', views.delete_account_view, name='delete_account'),
]
