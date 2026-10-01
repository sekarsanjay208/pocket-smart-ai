from database import find_products

products = find_products(
    "bedroom",
    "minimal",
    "chair"
)

print(products)