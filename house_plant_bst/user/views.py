from django.shortcuts import render

# Create your views here.


def signup_user(request):
    return render(request, 'user/signup_user.html')


def login_user(request):
    return render(request, 'user/login_user.html')
