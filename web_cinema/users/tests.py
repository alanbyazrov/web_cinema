from django.contrib.auth import authenticate, get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from users.forms import UserRegisterForm


User = get_user_model()


class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            phone="79998887766",
            first_name="John",
            last_name="Doe",
            password="testpass123",
        )
        self.assertEqual(user.phone, "79998887766")
        self.assertEqual(user.get_full_name(), "Doe John")
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        admin_user = User.objects.create_superuser(
            phone="79998880000",
            first_name="Admin",
            last_name="User",
            password="adminpass123",
        )
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)


class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            phone="79998887766",
            first_name="Test",
            last_name="User",
            password="testpass123",
        )

    def test_signup_view_get(self):
        response = self.client.get(reverse("users:signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/signup.html")
        self.assertIsInstance(response.context["form"], UserRegisterForm)

    def test_signup_view_post_success(self):
        data = {
            "phone": "79991112233",
            "first_name": "New",
            "last_name": "User",
            "password1": "complexpass123",
            "password2": "complexpass123",
        }
        response = self.client.post(reverse("users:signup"), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(phone="79991112233").exists())

    def test_signup_view_post_invalid(self):
        data = {
            "phone": "invalid",
            "first_name": "",
            "last_name": "",
            "password1": "pass",
            "password2": "pass2",
        }
        response = self.client.post(reverse("users:signup"), data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())

    def test_signup_view_post_duplicate_phone(self):
        data = {
            "phone": "79998887766",
            "first_name": "Duplicate",
            "last_name": "User",
            "password1": "testpass123",
            "password2": "testpass123",
        }
        response = self.client.post(reverse("users:signup"), data)
        self.assertEqual(response.status_code, 200)
        form = response.context["form"]
        self.assertFalse(form.is_valid())

    def test_logout_view(self):
        self.client.login(phone="79998887766", password="testpass123")
        response = self.client.post(reverse("users:logout"))
        self.assertEqual(response.status_code, 302)


class UserAuthenticationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone="79998887766",
            first_name="Test",
            last_name="User",
            password="testpass123",
        )

    def test_user_authentication(self):
        authenticated_user = authenticate(
            phone="79998887766", password="testpass123"
        )
        self.assertIsNotNone(authenticated_user)

        wrong_pass_user = authenticate(
            phone="79998887766", password="wrongpass"
        )
        self.assertIsNone(wrong_pass_user)