from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class UpdateUserView(UpdateView):
    form_class = CustomUserChangeForm
    success_url = '/user/profile/'
    template_name = 'registration/update.html'
    model = CustomUser

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.request.user.pk)


def profile(request):
    return render(request, 'user/profile.html')


# def signup(request):
#     return render(request, 'user/signup.html')


# def login(request):
#     return render(request, 'user/login.html')
