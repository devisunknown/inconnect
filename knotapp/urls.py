from django.urls import path

from . import views

urlpatterns = [
    path('', views.welcome, name='welcome'),
    path('terms/', views.terms_of_service, name='terms'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('password-reset/done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<str:uidb64>/<str:token>/', views.password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', views.password_reset_complete, name='password_reset_complete'),
    path('onboarding/', views.onboarding, name='onboarding'),
    path('matches/', views.matches, name='matches'),
    path('messages/', views.messages_list, name='messages'),
    path('chat/<int:chat_id>/', views.chat_room, name='chat_room'),
    path('chat/<int:chat_id>/action/', views.chat_action, name='chat_action'),
    path('start-chat/<int:user_id>/', views.start_chat, name='start_chat'),
    path('friend-request/<int:user_id>/', views.send_friend_request, name='send_friend_request'),
    path('notifications/', views.notifications, name='notifications'),
    path('search/users/', views.user_search, name='user_search'),
    path('respond-request/<int:request_id>/<str:action>/', views.respond_request, name='respond_request'),
    path('profile/', views.profile, name='profile'),
    path('profile/delete/', views.delete_profile, name='delete_profile'),
    path('profile/avatar/', views.upload_avatar, name='upload_avatar'),
    path('profile/bio/', views.update_bio, name='update_bio'),
    path('profile/about/', views.update_about, name='update_about'),
    path('profile/zoom/', views.update_zoom, name='update_zoom'),
    path('profile/<int:user_id>/', views.public_profile, name='public_profile'),
]
