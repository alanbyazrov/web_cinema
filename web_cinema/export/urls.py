from django.urls import path
from . import views

app_name = "export"

urlpatterns = [
    path(
        "export-recommendations-pdf/",
        views.export_recommendations_pdf,
        name="export_recommendations_pdf",
    ),
    path(
        "import-file/",
        views.import_csv,
        name="import_file",
    ),
]