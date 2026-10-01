import os

from dotenv import load_dotenv
from google import genai


# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")


# ==================================================
# CHECK API KEY
# ==================================================

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY is not set in the .env file"
    )


# ==================================================
# GEMINI CLIENT
# ==================================================

client = genai.Client(
    api_key=API_KEY
)


# ==================================================
# GENERATE HOME RECOMMENDATION EXPLANATION
# ==================================================

def generate_recommendation_explanation(
    room,
    style,
    budget,
    products
):

    # --------------------------------------------------
    # PREPARE PRODUCT INFORMATION
    # --------------------------------------------------

    if products:

        product_text = "\n".join(
            [
                f"- {product['name']} | "
                f"Category: {product['category']} | "
                f"Price: ₹{product['price']}"
                for product in products
            ]
        )

    else:

        product_text = "No products were selected."


    # --------------------------------------------------
    # GEMINI PROMPT
    # --------------------------------------------------

    prompt = f"""
You are PocketSmart AI,
a smart budget recommendation assistant.

The user wants to plan a {room}.

Style:
{style}

Budget:
₹{budget}

Recommended products from our product database:

{product_text}

Give a short and useful explanation
of why these products are suitable.

Requirements:

1. Do not invent products.
2. Do not change product prices.
3. Mention whether the recommendations
   stay within the budget.
4. Keep the response easy to understand.
5. Give practical advice to the user.
"""


    # --------------------------------------------------
    # CALL GEMINI
    # --------------------------------------------------

    try:

        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=prompt
        )

        if response.text:

            return response.text

        return create_fallback_explanation(
            room,
            style,
            budget,
            products
        )


    # --------------------------------------------------
    # GEMINI SERVER ERROR / API ERROR
    # --------------------------------------------------

    except Exception as e:

        print(
            "Gemini API temporarily unavailable:",
            str(e)
        )

        return create_fallback_explanation(
            room,
            style,
            budget,
            products
        )


# ==================================================
# FALLBACK EXPLANATION
# ==================================================

def create_fallback_explanation(
    room,
    style,
    budget,
    products
):

    total_cost = sum(
        product["price"]
        for product in products
    )


    remaining_budget = (
        budget - total_cost
    )


    # --------------------------------------------------
    # PRODUCT NAMES
    # --------------------------------------------------

    if products:

        product_names = ", ".join(
            product["name"]
            for product in products
        )

    else:

        product_names = "No products selected"


    # --------------------------------------------------
    # BUDGET STATUS
    # --------------------------------------------------

    if total_cost <= budget:

        budget_status = (
            f"The selected products are "
            f"within your budget. "
            f"You have ₹{remaining_budget:.0f} remaining."
        )

    else:

        budget_status = (
            "The selected products exceed "
            "the available budget."
        )


    # --------------------------------------------------
    # FALLBACK RESPONSE
    # --------------------------------------------------

    return f"""
PocketSmart AI Recommendation

Room:
{room}

Style:
{style}

Budget:
₹{budget:.0f}

Recommended products:
{product_names}

Total estimated cost:
₹{total_cost:.0f}

{budget_status}

These recommendations were selected
from the PocketSmart product database
based on your room, style and budget.
"""

def generate_jewelry_recommendation(
    occasion,
    style,
    budget,
    image_bytes,
    mime_type
):
    try:

        from google.genai import types

        prompt = f"""
You are PocketSmart AI, an intelligent jewelry recommendation assistant.

Analyze the uploaded outfit image and recommend suitable jewelry.

User details:

Occasion:
{occasion}

Preferred style:
{style}

Budget:
₹{budget}

Analyze the visible outfit carefully.

Consider:
1. Outfit color
2. Outfit style
3. Neckline if visible
4. Traditional or modern appearance
5. Suitable necklace type
6. Suitable earrings
7. Suitable bracelet or bangles
8. Suitable jewelry color
9. Whether gold, silver, diamond-style or fashion jewelry is appropriate

Give a practical recommendation.

Important:
- Do not invent details that cannot be seen.
- If the outfit color or neckline is unclear, say that it is unclear.
- Keep the recommendation within the user's budget.
- Do not recommend a specific product that is not provided.
- Give a simple explanation that a beginner can understand.

Format your answer with these sections:

Outfit Analysis:
...

Recommended Necklace:
...

Recommended Earrings:
...

Other Jewelry:
...

Jewelry Color:
...

Budget Advice:
...

Overall Recommendation:
...
"""

        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type
        )

        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=[
                prompt,
                image_part
            ]
        )

        return response.text

    except Exception as e:

        print(
            "Gemini jewelry image analysis failed:",
            str(e)
        )

        return (
            "Gemini image analysis is currently unavailable. "
            "Please try again later. "
            "The basic jewelry recommendation is still available."
        )