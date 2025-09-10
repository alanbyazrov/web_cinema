from io import BytesIO, StringIO
import os
import csv

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from django.db import transaction
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from movies.models import Genre, Movie, UserPreferences

from django.db.models import Count
from django.http import HttpResponse
from django.utils import timezone


def register_russian_fonts():
    """Регистрируем шрифты с поддержкой кириллицы"""
    from django.conf import settings

    try:
        # Путь к обычному шрифту Arial
        font_path = settings.BASE_DIR / "static" / "fonts" / "Arial.ttf"
        pdfmetrics.registerFont(TTFont("Arial", str(font_path)))

        # Путь к жирному шрифту Arial
        font_bold_path = (
            settings.BASE_DIR / "static" / "fonts" / "Arial_Bold.ttf"
        )
        if os.path.exists(font_bold_path):
            pdfmetrics.registerFont(TTFont("Arial-Bold", str(font_bold_path)))
        else:
            # Если нет жирного шрифта, используем обычный для bold
            pdfmetrics.registerFont(TTFont("Arial-Bold", str(font_path)))

    except Exception as e:
        print(f"Ошибка регистрации шрифтов: {e}")
        # Фолбэк на стандартные шрифты
        try:
            pdfmetrics.registerFont(TTFont("Helvetica", "Helvetica"))
            pdfmetrics.registerFont(TTFont("Helvetica-Bold", "Helvetica-Bold"))
        except Exception as e:
            print(e)


def export_recommendations_to_pdf(
    user, recommendations, filename="recommendations.pdf"
):
    """Экспорт рекомендаций в PDF с поддержкой кириллицы"""
    # Регистрируем русские шрифты
    register_russian_fonts()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()

    # Создаем кастомные стили с русскими шрифтами
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontName="Arial-Bold",
        fontSize=16,
        spaceAfter=30,
        alignment=1,  # center
        textColor=colors.darkblue,
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontName="Arial-Bold",
        fontSize=12,
        spaceAfter=12,
        textColor=colors.darkblue,
    )

    normal_style = ParagraphStyle(
        "NormalRussian", parent=styles["Normal"], fontName="Arial", fontSize=10
    )

    small_style = ParagraphStyle(
        "SmallRussian",
        parent=styles["Normal"],
        fontName="Arial",
        fontSize=8,
        textColor=colors.gray,
    )

    # Собираем элементы документа
    elements = []

    # Заголовок (используем простой текст вместо эмодзи)
    elements.append(
        Paragraph("ПЕРСОНАЛЬНЫЕ РЕКОМЕНДАЦИИ ФИЛЬМОВ", title_style)
    )
    elements.append(Spacer(1, 20))

    # Информация о пользователе
    elements.append(Paragraph(f"Пользователь: {user.phone}", heading_style))
    elements.append(
        Paragraph(
            f"Дата экспорта: {timezone.now().strftime('%d.%m.%Y %H:%M')}",
            small_style,
        )
    )
    elements.append(Spacer(1, 20))

    # Рекомендации
    if recommendations:
        elements.append(Paragraph("Рекомендуемые фильмы:", heading_style))

        # Создаем данные для таблицы
        table_data = [["Название", "Год", "Режиссер", "Жанры", "Лайки"]]

        for movie in recommendations:
            # Получаем количество лайков
            like_count = movie.liked_by.count()
            genres = ", ".join(
                [genre.name for genre in movie.genres.all()[:2]]
            )

            table_data.append(
                [
                    (
                        movie.title[:20] + "..."
                        if len(movie.title) > 20
                        else movie.title
                    ),
                    str(movie.year),
                    (
                        (movie.director or "-")[:15] + "..."
                        if movie.director and len(movie.director) > 15
                        else (movie.director or "-")
                    ),
                    genres[:20] + "..." if len(genres) > 20 else genres,
                    str(like_count),
                ]
            )

        # Создаем таблицу
        table = Table(
            table_data,
            colWidths=[
                1.8 * inch,
                0.5 * inch,
                1.0 * inch,
                1.2 * inch,
                0.5 * inch,
            ],
        )
        table.setStyle(
            TableStyle(
                [
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor("#2c3e50"),
                    ),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Arial-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 9),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                    (
                        "BACKGROUND",
                        (0, 1),
                        (-1, -1),
                        colors.HexColor("#ecf0f1"),
                    ),
                    ("FONTNAME", (0, 1), (-1, -1), "Arial"),
                    ("FONTSIZE", (0, 1), (-1, -1), 8),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        colors.HexColor("#bdc3c7"),
                    ),
                ]
            )
        )

        elements.append(table)
    else:
        elements.append(
            Paragraph("Нет рекомендаций для экспорта", normal_style)
        )

    elements.append(Spacer(1, 30))

    # Подвал
    elements.append(Paragraph("Сгенерировано Кинорекомендателем", small_style))

    # Собираем документ
    doc.build(elements)

    # Получаем PDF из buffer
    pdf = buffer.getvalue()
    buffer.close()

    return pdf


def export_recommendations_pdf_response(user, recommendations):
    """Создает HTTP response с PDF файлом"""
    pdf_content = export_recommendations_to_pdf(user, recommendations)

    response = HttpResponse(content_type="application/pdf")
    filename = (f"movie_recommendations_{user.phone}_"
                f"{timezone.now().strftime('%Y%m%d')}.pdf")
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.write(pdf_content)

    return response


def import_movies_from_csv(csv_file):
    """
    Импортирует фильмы из CSV файла
    Возвращает словарь с результатами импорта
    """
    results = {
        'imported_count': 0,
        'skipped_count': 0,
        'errors': []
    }

    try:
        # Читаем CSV файл
        data_set = csv_file.read().decode('UTF-8')
        io_string = StringIO(data_set)

        # Пропускаем заголовок
        next(io_string)

        # Создаем reader с правильным разделителем
        reader = csv.reader(io_string, delimiter=';')

        with transaction.atomic():
            for row_num, row in enumerate(reader, 2):  # row_num начинается с 2 (после заголовка)
                if len(row) < 7:
                    results['errors'].append(f"Строка {row_num}: Недостаточно данных")
                    results['skipped_count'] += 1
                    continue

                try:
                    title = row[0].strip()
                    description = row[1].strip()
                    year = int(row[2].strip())
                    director = row[3].strip()
                    country = row[4].strip()
                    image_url = row[5].strip()
                    genre_names = [g.strip() for g in row[6].split(',') if g.strip()]

                    # Проверяем, существует ли фильм с таким названием и годом
                    if Movie.objects.filter(title=title, year=year).exists():
                        results['skipped_count'] += 1
                        continue

                    # Создаем фильм
                    movie = Movie.objects.create(
                        title=title,
                        description=description,
                        year=year,
                        director=director,
                        country=country,
                        image_url=image_url
                    )

                    # Обрабатываем жанры
                    for genre_name in genre_names:
                        genre, created = Genre.objects.get_or_create(
                            name=genre_name,
                            defaults={'name': genre_name}
                        )
                        movie.genres.add(genre)

                    results['imported_count'] += 1

                except ValueError:
                    results['errors'].append(f"Строка {row_num}: Ошибка преобразования данных (год должен быть числом)")
                    results['skipped_count'] += 1
                except Exception as e:
                    results['errors'].append(f"Строка {row_num}: {str(e)}")
                    results['skipped_count'] += 1

    except csv.Error:
        results['errors'].append('Ошибка чтения CSV файла. Проверьте формат и разделители.')
    except UnicodeDecodeError:
        results['errors'].append('Ошибка декодирования файла. Убедитесь, что файл в кодировке UTF-8.')
    except Exception as e:
        results['errors'].append(f'Неожиданная ошибка при импорте: {str(e)}')

    return results


def validate_csv_file(csv_file):
    """
    Валидация CSV файла перед импортом
    """
    errors = []

    # Проверка расширения
    if not csv_file.name.endswith('.csv'):
        errors.append('Файл должен иметь расширение .csv')

    # Проверка размера (5MB)
    if csv_file.size > 5 * 1024 * 1024:
        errors.append('Размер файла не должен превышать 5MB')

    # Проверка наличия содержимого
    if csv_file.size == 0:
        errors.append('Файл пустой')

    return errors


def get_import_stats():
    """
    Получение статистики для отображения на странице импорта
    """
    return {
        'movie_count': Movie.objects.count(),
        'genre_count': Genre.objects.count(),
    }