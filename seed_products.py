import sqlite3

DATABASE_NAME = "pocketsmart.db"


products = [

    # -------------------------
    # Bedroom - Minimal
    # -------------------------

    ("Minimal Single Bed", "bedroom", "minimal", "bed", 12000),
    ("Minimal Study Chair", "bedroom", "minimal", "chair", 3000),
    ("Minimal Bedside Lamp", "bedroom", "minimal", "lamp", 1500),
    ("Minimal Wardrobe", "bedroom", "minimal", "wardrobe", 8500),
    ("Minimal Curtain", "bedroom", "minimal", "curtain", 2000),

    # -------------------------
    # Bedroom - Modern
    # -------------------------

    ("Modern Queen Bed", "bedroom", "modern", "bed", 18000),
    ("Modern Study Chair", "bedroom", "modern", "chair", 4500),
    ("Modern LED Lamp", "bedroom", "modern", "lamp", 2500),
    ("Modern Wardrobe", "bedroom", "modern", "wardrobe", 12000),
    ("Modern Curtain", "bedroom", "modern", "curtain", 3000),

    # -------------------------
    # Living Room - Modern
    # -------------------------

    ("Modern Sofa", "living_room", "modern", "sofa", 22000),
    ("Modern Coffee Table", "living_room", "modern", "table", 6000),
    ("Modern Floor Lamp", "living_room", "modern", "lamp", 3000),
    ("Modern TV Unit", "living_room", "modern", "tv_unit", 9000),

    # -------------------------
    # Living Room - Traditional
    # -------------------------

    ("Traditional Sofa", "living_room", "traditional", "sofa", 25000),
    ("Wooden Coffee Table", "living_room", "traditional", "table", 8000),
    ("Traditional Floor Lamp", "living_room", "traditional", "lamp", 3500),

    # -------------------------
    # Study Room - Minimal
    # -------------------------

    ("Minimal Study Table", "study_room", "minimal", "table", 5000),
    ("Minimal Study Chair", "study_room", "minimal", "chair", 3000),
    ("Bookshelf", "study_room", "minimal", "bookshelf", 4500),
    ("Study Lamp", "study_room", "minimal", "lamp", 1200),

    # -------------------------
    # Kitchen - Modern
    # -------------------------

    ("Modern Kitchen Table", "kitchen", "modern", "table", 7000),
    ("Kitchen Storage Cabinet", "kitchen", "modern", "cabinet", 10000),
    ("Kitchen Organizer", "kitchen", "modern", "organizer", 1800)
]


def insert_products():

    connection = sqlite3.connect(DATABASE_NAME)

    cursor = connection.cursor()

    cursor.executemany("""
        INSERT INTO products
        (name, room, style, category, price)
        VALUES (?, ?, ?, ?, ?)
    """, products)

    connection.commit()

    connection.close()

    print(f"{len(products)} products inserted successfully!")


if __name__ == "__main__":
    insert_products()