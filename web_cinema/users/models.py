from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("The Phone field must be set")
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser):
    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    first_name = models.CharField(
        verbose_name="имя",
        max_length=30,
        help_text="Имя пользователя",
    )
    last_name = models.CharField(
        verbose_name="фамилия",
        max_length=30,
        help_text="Фамилия пользователя",
    )
    phone = models.CharField(
        verbose_name="номер",
        unique=True,
        help_text="Номер пользователя",
        max_length=20,
    )
    is_staff = models.BooleanField(
        verbose_name="Сотрудник ли",
        default=False,
        help_text="Сотрудник проекта",
    )
    is_superuser = models.BooleanField(
        verbose_name="Админ ли",
        default=False,
        help_text="Администратор проекта",
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"Пользователь {self.phone}"

    def get_full_name(self):
        return f"{self.last_name} {self.first_name}".title()

    class Meta:
        db_table = "users"
        ordering = ["phone"]
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
