from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model


User = get_user_model()


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class ChangePassword(PasswordChangeForm):
    field_order = ('Старый пароль', 'Новый пароль', 'Новый пароль(повторно)')


class ResetPassword(PasswordResetForm):
    field_order = ('Адрес электронной почты')
