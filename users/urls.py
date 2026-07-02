from django.urls import path

from users.views import (
    AddBalanceView,
    LoginView,
    ProfileView,
    RefreshView,
    RegisterView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/refresh/', RefreshView.as_view(), name='refresh'),
    path('me/', ProfileView.as_view(), name='profile'),
    path('me/add-balance/', AddBalanceView.as_view(), name='add-balance'),
]
