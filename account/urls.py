from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('edit/', views.edit, name='edit'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('follow/<str:username>/', views.follow, name='follow'),
    path('users/', views.user_list, name='user_list'),
    path('send_friend_request/<int:to_user_id>/', views.send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:friendship_id>/', views.accept_friend_request, name='accept_friend_request'),
    path('reject_friend_request/<int:friendship_id>/', views.reject_friend_request, name='reject_friend_request'),
    path('friends/', views.friend_list, name='friend_list'),
    path('message/create/<int:recipient_id>/', views.create_message, name='create_message'),
    path('conversation/<int:recipient_id>/', views.conversation, name='conversation'),
    path('followers/<str:username>/', views.followers_view, name='followers'),
    path('following/<str:username>/', views.following_view, name='following'),
]
