from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.urls import reverse

from export.utils import export_recommendations_pdf_response, import_movies_from_csv, validate_csv_file, get_import_stats
from movies.models import UserPreferences
from movies.utils import get_recommendations


@login_required
def export_recommendations_pdf(request):
    """Экспорт рекомендаций в PDF"""
    try:
        # Получаем рекомендации
        recommendations = get_recommendations(request.user, limit=20)

        # Создаем PDF response
        return export_recommendations_pdf_response(
            request.user, recommendations
        )

    except UserPreferences.DoesNotExist:
        messages.error(request, "Сначала настройте предпочтения!")
        return redirect("movies:set_genre_preferences")
    except Exception as e:
        messages.error(request, f"Ошибка при экспорте: {str(e)}")
        return redirect("movies:recommendations")


@login_required
def import_csv(request):
    """
    Страница импорта CSV файлов с фильмами
    """
    if request.user.is_superuser:
        # Получаем статистику для отображения
        context = get_import_stats()

        if request.method == 'POST' and request.FILES.get('csv_file'):
            csv_file = request.FILES['csv_file']

            # Валидация файла
            validation_errors = validate_csv_file(csv_file)
            if validation_errors:
                for error in validation_errors:
                    messages.error(request, error)
                return render(request, 'export/import_csv.html', context)

            # Импорт данных из CSV
            results = import_movies_from_csv(csv_file)

            # Формируем сообщения на основе результатов
            if results['imported_count'] > 0:
                messages.success(request, f'Успешно импортировано {results["imported_count"]} фильмов')

            if results['skipped_count'] > 0:
                messages.warning(request, f'Пропущено {results["skipped_count"]} записей (дубликаты или ошибки)')

            if results['errors']:
                # Показываем только первые 5 ошибок
                error_msg = "Некоторые ошибки: " + "; ".join(results['errors'][:5])
                if len(results['errors']) > 5:
                    error_msg += f" ... и еще {len(results['errors']) - 5} ошибок"
                messages.error(request, error_msg)

            # Обновляем статистику после импорта
            context.update(get_import_stats())
            return render(request, 'export/import_csv.html', context)

        # GET запрос - показываем форму
        return render(request, 'export/import_csv.html', context)
    return redirect(reverse('movies:home'))