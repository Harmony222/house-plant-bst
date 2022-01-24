from django.urls import path

from . import views
from .views import SignUpView

app_name = "user"

urlpatterns = [
    path('signup/', SignUpView.as_view(), name='signup'),
    path('profile/', views.profile, name='profile'),
    # path('login/', views.login, name='login'),
]
