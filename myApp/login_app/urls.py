from django.urls import path     
from . import views
urlpatterns = [
    path('', views.index),	
    path('user/create', views.create),
    path('user/login', views.login),
    path('user/logout', views.logout),
    path('user/<int:user_id>/display', views.display_user),
    path('dashboard', views.dashboard),
    path('tennis/<int:opponent_id>/new', views.add_challenge),
    path('tennis/<int:opponent_id>/create', views.create_challenge),
    path('tennis/<int:challenge_id>/edit', views.edit_challenge),
    path('tennis/<int:challenge_id>/update', views.update_challenge),
    path('tennis/<int:challenge_id>/display', views.display_challenge),
    path('tennis/<int:challenge_id>/results', views.add_game_result),
    path('tennis/<int:challenge_id>/create_result', views.create_result),
    path('tennis/<int:challenge_id>/delete', views.delete_challenge),
    path('tennis/<int:challenge_id>/accept', views.accept_challenge),
    path('tennis/<int:challenge_id>/reject', views.reject_challenge),

    
]
