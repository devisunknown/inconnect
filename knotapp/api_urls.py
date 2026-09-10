from django.urls import path

from . import api_views

app_name = 'api'

urlpatterns = [
    path('auth/signup/', api_views.SignupView.as_view(), name='signup'),
    path('auth/login/', api_views.LoginView.as_view(), name='login'),
    path('auth/logout/', api_views.LogoutView.as_view(), name='logout'),
    path('auth/me/', api_views.MeView.as_view(), name='me'),
    path('interests/', api_views.InterestListView.as_view(), name='interest-list'),
    path('interests/select/', api_views.InterestSelectionView.as_view(), name='interest-select'),
    path('matches/', api_views.MatchesView.as_view(), name='matches'),
]
