from gemini_service import generate_recommendation_explanation


products = [
    {
        "name": "Compact Single Bed",
        "category": "bed",
        "price": 8000
    },
    {
        "name": "Basic Study Chair",
        "category": "chair",
        "price": 1500
    },
    {
        "name": "Basic Bedside Lamp",
        "category": "lamp",
        "price": 800
    }
]


result = generate_recommendation_explanation(
    room="bedroom",
    style="minimal",
    budget=13000,
    products=products
)


print("\nGemini Recommendation:\n")
print(result)