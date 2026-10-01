import sqlite3


DATABASE_NAME = "pocketsmart.db"


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_connection():

    connection = sqlite3.connect(
        DATABASE_NAME
    )

    connection.row_factory = sqlite3.Row

    return connection


# ==================================================
# CREATE DATABASE TABLES
# ==================================================

def create_table():

    connection = get_connection()

    cursor = connection.cursor()


    # ==================================================
    # CREATE PRODUCTS TABLE
    # ==================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS products (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            room TEXT NOT NULL,

            style TEXT NOT NULL,

            category TEXT NOT NULL,

            price REAL NOT NULL,

            amazon_url TEXT,

            flipkart_url TEXT,

            ikea_url TEXT
        )
        """
    )


    # ==================================================
    # CREATE USERS TABLE
    # ==================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            email TEXT NOT NULL UNIQUE,

            password TEXT NOT NULL
        )
        """
    )


    # ==================================================
    # CREATE HISTORY TABLE
    # ==================================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            planner_type TEXT NOT NULL,

            input_data TEXT NOT NULL,

            result_data TEXT NOT NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )


    connection.commit()

    connection.close()


# ==================================================
# ADD ECOMMERCE COLUMNS
# ==================================================

def add_ecommerce_columns():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "PRAGMA table_info(products)"
    )

    columns = [
        column["name"]
        for column in cursor.fetchall()
    ]


    # ------------------------------------------
    # AMAZON
    # ------------------------------------------

    if "amazon_url" not in columns:

        cursor.execute(
            """
            ALTER TABLE products
            ADD COLUMN amazon_url TEXT
            """
        )

        print(
            "Added amazon_url column."
        )


    # ------------------------------------------
    # FLIPKART
    # ------------------------------------------

    if "flipkart_url" not in columns:

        cursor.execute(
            """
            ALTER TABLE products
            ADD COLUMN flipkart_url TEXT
            """
        )

        print(
            "Added flipkart_url column."
        )


    # ------------------------------------------
    # IKEA
    # ------------------------------------------

    if "ikea_url" not in columns:

        cursor.execute(
            """
            ALTER TABLE products
            ADD COLUMN ikea_url TEXT
            """
        )

        print(
            "Added ikea_url column."
        )


    connection.commit()

    connection.close()


# ==================================================
# EXACT PRODUCT SEARCH
# ==================================================

def find_products(
    room,
    style,
    category
):

    connection = get_connection()

    products = connection.execute(
        """
        SELECT

            id,
            name,
            room,
            style,
            category,
            price,
            amazon_url,
            flipkart_url,
            ikea_url

        FROM products

        WHERE LOWER(room) = LOWER(?)

        AND LOWER(style) = LOWER(?)

        AND LOWER(category) = LOWER(?)

        ORDER BY price ASC
        """,

        (
            room,
            style,
            category
        )

    ).fetchall()

    connection.close()

    return [
        dict(product)
        for product in products
    ]


# ==================================================
# FALLBACK PRODUCT SEARCH
# ==================================================

def find_fallback_products(
    room,
    style,
    category
):

    connection = get_connection()


    # ==================================================
    # LEVEL 1
    # EXACT ROOM + STYLE + CATEGORY
    # ==================================================

    products = connection.execute(
        """
        SELECT

            id,
            name,
            room,
            style,
            category,
            price,
            amazon_url,
            flipkart_url,
            ikea_url

        FROM products

        WHERE LOWER(room) = LOWER(?)

        AND LOWER(style) = LOWER(?)

        AND LOWER(category) = LOWER(?)

        ORDER BY price ASC
        """,

        (
            room,
            style,
            category
        )

    ).fetchall()


    if products:

        connection.close()

        return [
            dict(product)
            for product in products
        ]


    # ==================================================
    # LEVEL 2
    # SAME ROOM + ANY STYLE + CATEGORY
    # ==================================================

    products = connection.execute(
        """
        SELECT

            id,
            name,
            room,
            style,
            category,
            price,
            amazon_url,
            flipkart_url,
            ikea_url

        FROM products

        WHERE LOWER(room) = LOWER(?)

        AND LOWER(category) = LOWER(?)

        ORDER BY price ASC
        """,

        (
            room,
            category
        )

    ).fetchall()


    if products:

        connection.close()

        return [
            dict(product)
            for product in products
        ]


    # ==================================================
    # LEVEL 3
    # SAME CATEGORY + ANY ROOM + ANY STYLE
    # ==================================================

    products = connection.execute(
        """
        SELECT

            id,
            name,
            room,
            style,
            category,
            price,
            amazon_url,
            flipkart_url,
            ikea_url

        FROM products

        WHERE LOWER(category) = LOWER(?)

        ORDER BY price ASC
        """,

        (
            category,
        )

    ).fetchall()

    connection.close()

    return [
        dict(product)
        for product in products
    ]


# ==================================================
# FIND CHEAPER PRODUCT
# ==================================================

def find_cheaper_product(
    room,
    style,
    category,
    max_price
):

    connection = get_connection()

    product = connection.execute(
        """
        SELECT

            id,
            name,
            room,
            style,
            category,
            price,
            amazon_url,
            flipkart_url,
            ikea_url

        FROM products

        WHERE LOWER(room) = LOWER(?)

        AND LOWER(style) = LOWER(?)

        AND LOWER(category) = LOWER(?)

        AND price <= ?

        ORDER BY price ASC

        LIMIT 1
        """,

        (
            room,
            style,
            category,
            max_price
        )

    ).fetchone()

    connection.close()


    if product:

        return dict(product)

    return None


# ==================================================
# ADD HISTORY
# ==================================================

def add_history(
    user_id,
    planner_type,
    input_data,
    result_data
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO history
        (
            user_id,
            planner_type,
            input_data,
            result_data
        )

        VALUES (?, ?, ?, ?)
        """,

        (
            user_id,
            planner_type,
            input_data,
            result_data
        )
    )

    connection.commit()

    history_id = cursor.lastrowid

    connection.close()

    return history_id


# ==================================================
# GET USER HISTORY
# ==================================================

def get_user_history(
    user_id
):

    connection = get_connection()

    history = connection.execute(
        """
        SELECT *

        FROM history

        WHERE user_id = ?

        ORDER BY created_at DESC
        """,

        (
            user_id,
        )

    ).fetchall()

    connection.close()

    return [
        dict(item)
        for item in history
    ]


# ==================================================
# GET SINGLE HISTORY
# ==================================================

def get_history_by_id(
    history_id,
    user_id
):

    connection = get_connection()

    history = connection.execute(
        """
        SELECT *

        FROM history

        WHERE id = ?

        AND user_id = ?
        """,

        (
            history_id,
            user_id
        )

    ).fetchone()

    connection.close()


    if history:

        return dict(history)

    return None


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    create_table()

    add_ecommerce_columns()

    print(
        "Database tables are ready."
    )