from database import find_cheaper_product


product = find_cheaper_product(
    "bedroom",
    "minimal",
    "chair",
    3500
)

print(product)