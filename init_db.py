# init_db.py
import json
from models import create_tables
from database import add_category, add_sausage

# Load sausage data from JSON
with open("sausages_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Create DB tables
create_tables()

# Insert categories and sausages
category_ids = {}

for item in data:
    cat = item["category"]
    if cat not in category_ids:
        add_category(cat)
    category_ids[cat] = None  # Will fetch real ID later

# Get updated category IDs
from database import get_all_categories
cats = get_all_categories()
for cat_id, cat_name in cats:
    category_ids[cat_name] = cat_id

for item in data:
    add_sausage(
        name=item["name"],
        category_id=category_ids[item["category"]],
        grade=item.get("grade", ""),
        packaging=item.get("packaging", ""),
        casing=item.get("casing", ""),
        shelf_life=item.get("shelf_life", ""),
        price=float(item["price"]),
        image_path=f"images/{item['image']}"
    )

print("Database initialized with sausages.")
