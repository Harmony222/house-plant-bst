from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import TemplateView
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import authenticate, login


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('user:profile')

    def form_valid(self, form):
        """Overrides method to login user after successful signup"""
        # save new user
        self.object = form.save()
        # get username and password from POST
        username = self.request.POST['username']
        password = self.request.POST['password1']
        # authenticate user first, then login and redirect to profile page
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return redirect(self.success_url)


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
