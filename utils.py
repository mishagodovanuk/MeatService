def format_sausage_text(s):
    lines = [
        f"<b>{s['name']}</b>",
        f"Гатунок: {s['grade']}",
        f"Упаковка: {s['packaging']}",
        f"Оболонка: {s['casing']}",
        f"Термін: {s['shelf_life']}",
        f"Ціна: <b>{s['price']} грн/кг</b>"
    ]
    return "\n".join(lines)


def get_image_path(image_name):
    from config import IMAGE_FOLDER
    return f"{image_name}"