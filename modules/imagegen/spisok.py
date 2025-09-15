from PIL import Image, ImageDraw, ImageFont
import math

def generate_image_with_text(
    text_lines,
    image_path,
    background_path="background.png",
    columns=2,
    highlight_name=None,
    margin_left=20,
    margin_top=20
):
    # Открываем фон
    img = Image.open(background_path).convert("RGB")
    draw = ImageDraw.Draw(img)

    font = ImageFont.truetype("inter.ttf", 24)
    line_height = 35

    # Считаем количество строк в колонке
    rows_per_column = math.ceil(len(text_lines) / columns)

    # Определяем максимальную ширину текста
    max_text_width = max(draw.textlength(line, font=font) for line in text_lines)

    # Ширина колонки = максимальная ширина + небольшой запас
    col_width = int(max_text_width + 50)

    # Проверяем, помещается ли текст по ширине и высоте фона
    bg_width, bg_height = img.size
    needed_width = margin_left + col_width * columns + margin_left
    needed_height = margin_top + rows_per_column * line_height + margin_top

    if needed_width > bg_width or needed_height > bg_height:
        print(f"ВНИМАНИЕ: текст может не поместиться на фоне! Фон: {bg_width}x{bg_height}, нужно: {needed_width}x{needed_height}")

    # Цвета
    text_color = (30, 30, 30)
    highlight_bg = (255, 255, 150)

    # Рисуем текст
    for idx, line in enumerate(text_lines):
        col = idx // rows_per_column
        row = idx % rows_per_column

        x = margin_left + col * col_width
        y = margin_top + row * line_height

        # Подсветка
        if highlight_name and highlight_name.lower() in line.lower():
            bbox = draw.textbbox((x, y), line, font=font)
            draw.rectangle(bbox, fill=highlight_bg)

        draw.text((x, y), line, font=font, fill=text_color)

    img.save(image_path)
    return image_path

sample_text = [ "Список участников:", "1. Иван Иванов", "2. Пётр Петров", "3. Сергей Сергеев", "4. Валерий Орлов", "5. Константин Морозов Тестимотступович ИС-12-25", "6. Максим Зайцев", "7. Дмитрий Лебедев", "8. Андрей Никитин", "9. Тимофей Рыбаков", "10. Юрий Кузнецов", "11. Владимир Петров", "12. Анатолий Федотов", "13. Алексей Морозов", "14. Сергей Ушаков", "15. Николай Ефимов", "16. Павел Якимов", "17. Евгений Соколов", "18. Василий Орлов", "19. Виктор Журавлёв", "20. Роман Белов", "21. Константин Лебедев", "22. Дмитрий Никитин", "23. Тимофей Морозов", "24. Андрей Петров", "25. Юрий Кузнецов", "26. Анатолий Рыбаков", "27. Алексей Ушаков", "28. Николай Федотов", "29. Максим Зайцев", "30. Павел Некитин", "31. Евгений Кузнецов", "32. Роман Якимов", "33. Сергей Морозов", "34. Василий Орлов", "35. Владимир Никитин", "36. Дмитрий Журавлёв", "37. Константин Соколов", "38. Максим Белов", "39. Алексей Кузнецов", "40. Тимофей Петров", "41. Василий Рыбаков", "42. Андрей Якимов", "43. Юрий Никитин", "44. Павел Журавлёв", "45. Евгений Морозов", "46. Николай Ушаков", "47. Владимир Белов", "48. Роман Соколов", "49. Алексей Зайцев", "50. Константин Лебедев", "51. Максим Петров", "52. Дмитрий Орлов", "53. Тимофей Федотов", "54. Андрей Якимов" ]


generate_image_with_text(
    sample_text,
    "output_on_background_custom.png",
    background_path="background.png",
    columns=2,
    highlight_name="Анатолий",
    margin_left=180,
    margin_top=360
)
