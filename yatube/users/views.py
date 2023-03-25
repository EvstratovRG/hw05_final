from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.core.mail import send_mail

from .forms import CreationForm, ChangePassword, ResetPassword


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('posts:index')
    template_name = 'users/signup.html'


class PassChange(CreateView):
    form_class = ChangePassword
    success_url = reverse_lazy('user:password_change_done')
    template_name = 'users/password_change_done.html'


class PassReser(CreateView):
    form_class = ResetPassword
    success_url = reverse_lazy('user:password_reset_done')
    template_name = 'users/password_reset_done.html'


send_mail(
    'Тема письма',
    'Текст письма.',
    'from@example.com',  # Это поле "От кого"
    ['to@example.com'],  # Это поле "Кому" (можно указать список адресов)
    fail_silently=False,  # Сообщать об ошибках («молчать ли об ошибках?»)
)
