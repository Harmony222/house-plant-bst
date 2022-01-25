from django.urls import path

from .views import SignUpView, UpdateUserView
from django.views.generic import TemplateView

app_name = "user"

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path(
        'profile/',
        TemplateView.as_view(template_name='user/profile.html'),
        name='profile',
    ),
    path('update/', UpdateUserView.as_view(), name='update_user'),
]
