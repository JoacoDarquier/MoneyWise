from django.urls import path, include
from django.contrib.auth import views as auth_views

from users.views import (
    index,
    register,
)

urlpatterns = [
    path('', index, name='index'),
    path('register/', register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('', include('core.urls')),
]