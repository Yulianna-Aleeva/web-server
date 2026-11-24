from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView
from .forms import CustomAuthenticationForm, CustomUserCreationForm, CustomUserChangeForm


class RegisterView(CreateView):
    template_name = 'users/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('catalog:home')

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        self.send_welcome_email(user.email)
        return super().form_valid(form)

    def send_welcome_email(self, user_email):
        subject = 'Добро пожаловать в магазин MY-RELAX!'
        message = 'Спасибо за регистрацию! Желаем вам приятных покупок и уютного отдыха.'
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user_email],
            fail_silently=False,
        )


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = CustomAuthenticationForm


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('catalog:home')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = CustomUserChangeForm
    template_name = 'users/profile_form.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user
