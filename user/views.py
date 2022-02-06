from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import TemplateView
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from django.contrib.auth.mixins import LoginRequiredMixin


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'


class UpdateUserView(LoginRequiredMixin, UpdateView):
    login_url = reverse_lazy('login')
    form_class = CustomUserChangeForm
    success_url = reverse_lazy('user:profile')
    template_name = 'registration/update.html'
    model = CustomUser

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.request.user.pk)


class ProfileView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('login')
    template_name = 'user/profile.html'
