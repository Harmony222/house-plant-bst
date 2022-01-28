from django.urls import path

from .views import SignUpView, UpdateUserView, ProfileView

app_name = "user"

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path(
        'profile/',
        ProfileView.as_view(),
        name='profile',
    ),
    path('update/', UpdateUserView.as_view(), name='update_user'),
]
