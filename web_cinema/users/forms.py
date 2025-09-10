from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


User = get_user_model()


class UserRegisterForm(UserCreationForm):
    phone = forms.CharField(
        max_length=20,
        label="Телефон",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "+7 (999) 999 99 99",
                "id": "id_phone",  # Добавляем ID
            }
        ),
    )

    first_name = forms.CharField(
        label="Имя", widget=forms.TextInput(attrs={"class": "form-control"})
    )

    last_name = forms.CharField(
        label="Фамилия",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Стилизуем остальные поля для Bootstrap
        for field_name in self.fields:
            if field_name not in ["password1", "password2"]:
                self.fields[field_name].widget.attrs.update(
                    {"class": "form-control"}
                )

        # Специальная обработка полей паролей
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})


class MyLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Телефон",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "+7 (999) 999 99 99",
                "id": "id_username",  # Добавляем ID
            }
        ),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Введите ваш пароль",
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super(MyLoginForm, self).__init__(*args, **kwargs)
        # Переименовываем поле username для отображения
        self.fields["username"].label = "Телефон"
