from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

# Remove app_name to use URL names without namespace

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]