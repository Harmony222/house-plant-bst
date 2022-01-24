from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from .forms import CustomUserCreationForm

# Create your views here.


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


def profile(request):
    return render(request, 'user/profile.html')


# def signup(request):
#     return render(request, 'user/signup.html')


# def login(request):
#     return render(request, 'user/login.html')
