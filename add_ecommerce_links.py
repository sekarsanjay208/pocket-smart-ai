import urllib.parse

from database import get_connection


# ==================================================
# CREATE SEARCH URLS
# ==================================================

def create_links(product_name):

    encoded_name = urllib.parse.quote_plus(
        product_name
    )

    amazon_url = (
        "https://www.amazon.in/s?k="
        + encoded_name
    )

    flipkart_url = (
        "https://www.flipkart.com/search?q="
        + encoded_name
    )

    ikea_url = (
        "https://www.ikea.com/in/en/search/"
        + encoded_name
    )

    return (
        amazon_url,
        flipkart_url,
        ikea_url
    )


# ==================================================
# UPDATE PRODUCTS
# ==================================================

def update_product_links():

    connection = get_connection()

    products = connection.execute(
        """
        SELECT id, name
        FROM products
        """
    ).fetchall()

    for product in products:

        amazon_url, flipkart_url, ikea_url = (
            create_links(product["name"])
        )

        connection.execute(
            """
            UPDATE products

            SET
                amazon_url = ?,
                flipkart_url = ?,
                ikea_url = ?

            WHERE id = ?
            """,
            (
                amazon_url,
                flipkart_url,
                ikea_url,
                product["id"]
            )
        )

    connection.commit()

    connection.close()

    print(
        f"Updated ecommerce links for "
        f"{len(products)} products."
    )


# ==================================================
# RUN
# ==================================================

if __name__ == "__main__":

    update_product_links()