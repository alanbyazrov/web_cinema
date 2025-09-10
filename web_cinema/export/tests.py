from export.utils import export_recommendations_to_pdf
from movies.models import Genre, Movie

from django.contrib.auth import get_user_model
from django.test import TestCase


User = get_user_model()


class ExportUtilsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            phone="79998887766",
            first_name="Test",
            last_name="User",
            password="testpass123",
        )
        self.genre = Genre.objects.create(name="Драма")
        self.movie = Movie.objects.create(
            title="Тестовый фильм", year=2023, director="Тестовый режиссер"
        )
        self.movie.genres.add(self.genre)

    def test_export_recommendations_to_pdf(self):
        recommendations = [self.movie]

        try:
            pdf_content = export_recommendations_to_pdf(
                self.user, recommendations
            )
            self.assertIsInstance(pdf_content, bytes)
            self.assertGreater(len(pdf_content), 0)
        except Exception as e:
            self.fail(f"PDF export failed: {e}")

    def test_export_empty_recommendations(self):
        recommendations = []

        try:
            pdf_content = export_recommendations_to_pdf(
                self.user, recommendations
            )
            self.assertIsInstance(pdf_content, bytes)
        except Exception as e:
            self.fail(f"PDF export failed: {e}")
