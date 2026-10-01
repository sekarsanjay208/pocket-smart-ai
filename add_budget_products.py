from database import get_connection


products = [
    {
        "name": "Compact Single Bed",
        "room": "bedroom",
        "style": "minimal",
        "category": "bed",
        "price": 8000
    },
    {
        "name": "Basic Study Chair",
        "room": "bedroom",
        "style": "minimal",
        "category": "chair",
        "price": 1500
    },
    {
        "name": "Basic Bedside Lamp",
        "room": "bedroom",
        "style": "minimal",
        "category": "lamp",
        "price": 800
    },

    {
        "name": "Budget Modern Bed",
        "room": "bedroom",
        "style": "modern",
        "category": "bed",
        "price": 12000
    },
    {
        "name": "Budget Modern Chair",
        "room": "bedroom",
        "style": "modern",
        "category": "chair",
        "price": 2500
    },
    {
        "name": "Budget LED Lamp",
        "room": "bedroom",
        "style": "modern",
        "category": "lamp",
        "price": 1200
    },

    {
        "name": "Compact Sofa",
        "room": "living",
        "style": "modern",
        "category": "sofa",
        "price": 14000
    },
    {
        "name": "Budget Coffee Table",
        "room": "living",
        "style": "modern",
        "category": "table",
        "price": 3500
    },
    {
        "name": "Basic Floor Lamp",
        "room": "living",
        "style": "modern",
        "category": "lamp",
        "price": 1800
    },

    {
        "name": "Budget Study Table",
        "room": "study",
        "style": "minimal",
        "category": "table",
        "price": 3500
    },
    {
        "name": "Basic Study Chair",
        "room": "study",
        "style": "minimal",
        "category": "chair",
        "price": 1500
    },
    {
        "name": "Compact Bookshelf",
        "room": "study",
        "style": "minimal",
        "category": "bookshelf",
        "price": 2500
    }
]


conn = get_connection()
cursor = conn.cursor()

added = 0
skipped = 0

for product in products:

    cursor.execute(
        """
        SELECT id
        FROM products
        WHERE name = ?
        """,
        (product["name"],)
    )

    existing = cursor.fetchone()

    if existing:
        skipped += 1
        continue

    cursor.execute(
        """
        INSERT INTO products
        (name, room, style, category, price)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            product["name"],
            product["room"],
            product["style"],
            product["category"],
            product["price"]
        )
    )

    added += 1


conn.commit()
conn.close()

print(f"Products added: {added}")
print(f"Products already existed: {skipped}")
print("Budget-friendly products processed successfully.")