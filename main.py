import json
import os

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    Request,
    UploadFile,
    File,
    Form
)

from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel, Field

from database import (
    get_connection,
    create_table,
    add_ecommerce_columns,
    find_products,
    find_fallback_products,
    find_cheaper_product,
    add_history,
    get_user_history,
    get_history_by_id
)

# ==================================================
# SEED PRODUCTS
# ==================================================

# ==================================================
# SEED PRODUCTS
# ==================================================

from seed_products import insert_products
from add_ecommerce_links import update_product_links

from gemini_service import (
    generate_recommendation_explanation,
    generate_jewelry_recommendation
)

from password_utils import (
    hash_password,
    verify_password
)


# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================

load_dotenv()


# ==================================================
# INITIALIZE DATABASE
# ==================================================

# ==================================================
# INITIALIZE DATABASE
# ==================================================

create_table()
add_ecommerce_columns()
insert_products()
update_product_links()


# ==================================================
# GET SECRET KEY
# ==================================================

SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY is not set in the .env file"
    )


# ==================================================
# CREATE FASTAPI APP
# ==================================================

app = FastAPI()


# ==================================================
# SESSION MIDDLEWARE
# ==================================================

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY
)


# ==================================================
# STATIC FILES
# ==================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# ==================================================
# TEMPLATES
# ==================================================

templates = Jinja2Templates(
    directory="templates"
)


# ==================================================
# REQUEST MODELS
# ==================================================

class HomeRequest(BaseModel):

    budget: float = Field(gt=0)
    room: str
    style: str
    required_items: list[str]


class RegisterRequest(BaseModel):

    name: str
    email: str
    password: str


class LoginRequest(BaseModel):

    email: str
    password: str


class PartyRequest(BaseModel):

    budget: float = Field(gt=0)
    guests: int = Field(gt=0)
    event_type: str
    venue: str


# ==================================================
# HOME / LANDING PAGE
# ==================================================

@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# ==================================================
# HOME PLANNER PAGE
# ==================================================

@app.get(
    "/home-planner",
    response_class=HTMLResponse
)
def home_planner_page(request: Request):

    if "user_id" not in request.session:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="home.html"
    )


# ==================================================
# REGISTER PAGE
# ==================================================

@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="register.html"
    )


# ==================================================
# LOGIN PAGE
# ==================================================

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )


# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "message": "PocketSmart AI backend is running"
    }


# ==================================================
# HOME RECOMMENDATION
# FALLBACK + SMART BUDGET SELECTION
# ==================================================

@app.post("/generate-home")
def generate_home(
    request: HomeRequest,
    http_request: Request
):

    recommended_products = []

    unavailable_items = []

    total_cost = 0

    available_items = []

    # ==================================================
    # FIND PRODUCTS USING FALLBACK SYSTEM
    # ==================================================

    for item in request.required_items:

        products = find_fallback_products(
            request.room,
            request.style,
            item
        )

        # ------------------------------------------
        # NO PRODUCT FOUND EVEN AFTER FALLBACK
        # ------------------------------------------

        if not products:

            unavailable_items.append(item)

            continue

        # ------------------------------------------
        # PRODUCTS ARE SORTED BY PRICE
        # ------------------------------------------

        cheapest_product = products[0]

        available_items.append({
            "item": item,
            "product": cheapest_product
        })

    # ==================================================
    # SORT PRODUCTS BY CHEAPEST PRICE
    # ==================================================

    available_items.sort(
        key=lambda x: x["product"]["price"]
    )

    # ==================================================
    # SELECT PRODUCTS WITHIN BUDGET
    # ==================================================

    for item_data in available_items:

        item = item_data["item"]

        product = item_data["product"]

        remaining_budget = (
            request.budget - total_cost
        )

        # ------------------------------------------
        # PRODUCT FITS THE BUDGET
        # ------------------------------------------

        if product["price"] <= remaining_budget:

            recommended_products.append(
                product
            )

            total_cost += product["price"]

        # ------------------------------------------
        # PRODUCT DOES NOT FIT
        # ------------------------------------------

        else:

            unavailable_items.append(
                item
            )

    # ==================================================
    # GEMINI AI EXPLANATION
    # ==================================================

    ai_explanation = generate_recommendation_explanation(

        room=request.room,

        style=request.style,

        budget=request.budget,

        products=recommended_products

    )

    # ==================================================
    # CREATE FINAL RESULT
    # ==================================================

    result = {

        "success": True,

        "room":
            request.room,

        "style":
            request.style,

        "budget":
            request.budget,

        "recommended_products":
            recommended_products,

        "total_cost":
            total_cost,

        "remaining_budget":
            request.budget - total_cost,

        "unavailable_items":
            unavailable_items,

        "ai_explanation":
            ai_explanation

    }

    # ==================================================
    # SAVE HOME PLANNER HISTORY
    # ==================================================

    user_id = http_request.session.get(
        "user_id"
    )

    if user_id:

        input_data = {

            "budget":
                request.budget,

            "room":
                request.room,

            "style":
                request.style,

            "required_items":
                request.required_items

        }

        history_id = add_history(

            user_id=user_id,

            planner_type="home",

            input_data=json.dumps(
                input_data
            ),

            result_data=json.dumps(
                result
            )

        )

        print(
            f"Home history saved successfully. ID: {history_id}"
        )

    else:

        print(
            "No logged-in user found. "
            "Home history not saved."
        )

    # ==================================================
    # RETURN RESULT
    # ==================================================

    return result


# ==================================================
# REGISTER USER
# ==================================================

@app.post("/register")
def register_user(
    request: RegisterRequest
):

    connection = get_connection()

    try:

        hashed_password = hash_password(
            request.password
        )

        connection.execute(
            """
            INSERT INTO users
            (name, email, password)
            VALUES (?, ?, ?)
            """,
            (
                request.name,
                request.email,
                hashed_password
            )
        )

        connection.commit()

        return {

            "success": True,

            "message":
                "Account created successfully"

        }

    except Exception as e:

        print(
            "Registration error:",
            str(e)
        )

        if (
            "UNIQUE constraint failed: users.email"
            in str(e)
        ):

            return {

                "success": False,

                "message":
                    "Email already registered. Please login instead."

            }

        return {

            "success": False,

            "message":
                "Registration failed. Please try again."

        }

    finally:

        connection.close()


# ==================================================
# LOGIN USER
# ==================================================

@app.post("/login")
def login_user(
    request: LoginRequest,
    http_request: Request
):

    connection = get_connection()

    try:

        user = connection.execute(
            """
            SELECT id, name, email, password
            FROM users
            WHERE email = ?
            """,
            (
                request.email,
            )
        ).fetchone()

        if user is None:

            return {

                "success": False,

                "message":
                    "Invalid email or password."

            }

        stored_password = user["password"]

        password_is_valid = False

        # ==================================================
        # VERIFY BCRYPT PASSWORD
        # ==================================================

        try:

            password_is_valid = verify_password(
                request.password,
                stored_password
            )

        except Exception:

            password_is_valid = False

        # ==================================================
        # OLD PASSWORD COMPATIBILITY
        # ==================================================

        if not password_is_valid:

            if stored_password == request.password:

                password_is_valid = True

                new_hashed_password = hash_password(
                    request.password
                )

                connection.execute(
                    """
                    UPDATE users
                    SET password = ?
                    WHERE id = ?
                    """,
                    (
                        new_hashed_password,
                        user["id"]
                    )
                )

                connection.commit()

                print(
                    f"Old password migrated to bcrypt "
                    f"for user ID: {user['id']}"
                )

        # ==================================================
        # INVALID LOGIN
        # ==================================================

        if not password_is_valid:

            return {

                "success": False,

                "message":
                    "Invalid email or password."

            }

        # ==================================================
        # CREATE SESSION
        # ==================================================

        http_request.session["user_id"] = (
            user["id"]
        )

        http_request.session["user_name"] = (
            user["name"]
        )

        http_request.session["user_email"] = (
            user["email"]
        )

        return {

            "success": True,

            "message":
                "Login successful",

            "user": {

                "id":
                    user["id"],

                "name":
                    user["name"],

                "email":
                    user["email"]

            }

        }

    finally:

        connection.close()


# ==================================================
# SESSION INFORMATION
# ==================================================

@app.get("/session-info")
def session_info(request: Request):

    user_id = request.session.get(
        "user_id"
    )

    if not user_id:

        return {

            "logged_in": False

        }

    return {

        "logged_in": True,

        "user": {

            "id":
                request.session.get(
                    "user_id"
                ),

            "name":
                request.session.get(
                    "user_name"
                ),

            "email":
                request.session.get(
                    "user_email"
                )

        }

    }


# ==================================================
# DASHBOARD
# ==================================================

@app.get(
    "/dashboard",
    response_class=HTMLResponse
)
def dashboard(request: Request):

    user_id = request.session.get(
        "user_id"
    )

    if not user_id:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return templates.TemplateResponse(

        request=request,

        name="dashboard.html",

        context={

            "user_name":
                request.session.get(
                    "user_name"
                ),

            "user_email":
                request.session.get(
                    "user_email"
                )

        }

    )


# ==================================================
# PARTY PLANNER PAGE
# ==================================================

@app.get(
    "/party",
    response_class=HTMLResponse
)
def party_page(request: Request):

    if "user_id" not in request.session:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return templates.TemplateResponse(

        request=request,

        name="party.html"

    )


# ==================================================
# PARTY RECOMMENDATION + HISTORY
# ==================================================

@app.post("/generate-party")
def generate_party(
    request: PartyRequest,
    http_request: Request
):

    budget = request.budget

    guests = request.guests

    # ==================================================
    # BUDGET ALLOCATION
    # ==================================================

    venue_budget = budget * 0.30

    food_budget = budget * 0.40

    decoration_budget = budget * 0.20

    miscellaneous_budget = budget * 0.10

    # ==================================================
    # TOTAL COST
    # ==================================================

    total_cost = (
        venue_budget
        + food_budget
        + decoration_budget
        + miscellaneous_budget
    )

    # ==================================================
    # AI EXPLANATION
    # ==================================================

    ai_explanation = f"""
For your {request.event_type} with {guests} guests
at a {request.venue} venue, your ₹{budget:.0f} budget
can be planned as follows:

Venue: approximately ₹{venue_budget:.0f}

Food: approximately ₹{food_budget:.0f}

Decoration: approximately ₹{decoration_budget:.0f}

Miscellaneous: approximately ₹{miscellaneous_budget:.0f}

The estimated plan stays within your budget.
"""

    # ==================================================
    # CREATE RESULT
    # ==================================================

    result = {

        "success": True,

        "event_type":
            request.event_type,

        "guests":
            guests,

        "venue":
            request.venue,

        "budget":
            budget,

        "venue_budget":
            venue_budget,

        "food_budget":
            food_budget,

        "decoration_budget":
            decoration_budget,

        "miscellaneous_budget":
            miscellaneous_budget,

        "total_cost":
            total_cost,

        "ai_explanation":
            ai_explanation

    }

    # ==================================================
    # SAVE PARTY HISTORY
    # ==================================================

    user_id = http_request.session.get(
        "user_id"
    )

    if user_id:

        input_data = {

            "budget":
                request.budget,

            "guests":
                request.guests,

            "event_type":
                request.event_type,

            "venue":
                request.venue

        }

        history_id = add_history(

            user_id=user_id,

            planner_type="party",

            input_data=json.dumps(
                input_data
            ),

            result_data=json.dumps(
                result
            )

        )

        print(
            f"Party history saved successfully. ID: {history_id}"
        )

    else:

        print(
            "No logged-in user found. "
            "Party history not saved."
        )

    return result


# ==================================================
# JEWELRY PLANNER PAGE
# ==================================================

@app.get(
    "/jewelry",
    response_class=HTMLResponse
)
def jewelry_page(request: Request):

    if "user_id" not in request.session:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return templates.TemplateResponse(

        request=request,

        name="jewelry.html"

    )


# ==================================================
# JEWELRY RECOMMENDATION + IMAGE + HISTORY
# ==================================================

@app.post("/generate-jewelry")
async def generate_jewelry(

    http_request: Request,

    budget: float = Form(...),

    occasion: str = Form(...),

    style: str = Form(...),

    outfit: UploadFile | None = File(None)

):

    # ==================================================
    # BASIC VALIDATION
    # ==================================================

    if budget <= 0:

        return {

            "success": False,

            "message":
                "Budget must be greater than 0."

        }

    # ==================================================
    # IMAGE INFORMATION
    # ==================================================

    image_received = False

    image_filename = None

    image_content_type = None

    image_bytes = None

    if outfit:

        print(
            "Image received:",
            outfit.filename
        )

        print(
            "Image type:",
            outfit.content_type
        )

        # ------------------------------------------
        # VALIDATE IMAGE TYPE
        # ------------------------------------------

        allowed_types = [
            "image/jpeg",
            "image/png"
        ]

        if outfit.content_type not in allowed_types:

            return {

                "success": False,

                "message":
                    "Only JPG and PNG images are allowed."

            }

        # ------------------------------------------
        # READ IMAGE
        # ------------------------------------------

        image_bytes = await outfit.read()

        # ------------------------------------------
        # CHECK IMAGE SIZE
        # ------------------------------------------

        max_size = 5 * 1024 * 1024

        if len(image_bytes) > max_size:

            return {

                "success": False,

                "message":
                    "Image size must be less than 5 MB."

            }

        image_received = True

        image_filename = outfit.filename

        image_content_type = outfit.content_type

    # ==================================================
    # JEWELRY RECOMMENDATION
    # ==================================================

    if style == "traditional":

        recommendation = (
            "Traditional gold necklace with "
            "matching earrings"
        )

    elif style == "modern":

        recommendation = (
            "Modern layered necklace with "
            "elegant earrings"
        )

    elif style == "minimal":

        recommendation = (
            "Minimal pendant necklace with "
            "small earrings"
        )

    elif style == "bridal":

        recommendation = (
            "Bridal necklace set with "
            "matching earrings"
        )

    elif style == "elegant":

        recommendation = (
            "Elegant diamond-style necklace with "
            "matching earrings"
        )

    else:

        recommendation = (
            "Classic necklace and matching earrings"
        )

    # ==================================================
    # BUDGET ADVICE
    # ==================================================

    if budget < 5000:

        budget_advice = (
            "Consider lightweight jewelry, "
            "silver jewelry or affordable "
            "fashion jewelry."
        )

    elif budget < 15000:

        budget_advice = (
            "You can consider a good-quality "
            "necklace and matching earrings "
            "within this range."
        )

    else:

        budget_advice = (
            "Your budget allows you to consider "
            "premium jewelry sets."
        )

    # ==================================================
    # AI EXPLANATION
    # ==================================================

    if image_received:

        ai_explanation = generate_jewelry_recommendation(

            occasion=occasion,

            style=style,

            budget=budget,

            image_bytes=image_bytes,

            mime_type=image_content_type

        )

    else:

        ai_explanation = f"""
For a {occasion} occasion with a
{style} style and a budget of
₹{budget:.0f}:

Recommended:

{recommendation}

Budget advice:

{budget_advice}

No outfit image was uploaded.

Choose jewelry that complements your outfit,
occasion and personal style while keeping the
total purchase within your planned budget.
"""

    # ==================================================
    # CREATE RESULT
    # ==================================================

    result = {

        "success": True,

        "occasion":
            occasion,

        "style":
            style,

        "budget":
            budget,

        "recommendation":
            recommendation,

        "image_received":
            image_received,

        "image_filename":
            image_filename,

        "ai_explanation":
            ai_explanation

    }

    # ==================================================
    # SAVE JEWELRY HISTORY
    # ==================================================

    user_id = http_request.session.get(
        "user_id"
    )

    if user_id:

        input_data = {

            "budget":
                budget,

            "occasion":
                occasion,

            "style":
                style,

            "outfit_image":
                image_filename

        }

        history_id = add_history(

            user_id=user_id,

            planner_type="jewelry",

            input_data=json.dumps(
                input_data
            ),

            result_data=json.dumps(
                result
            )

        )

        print(
            f"Jewelry history saved successfully. ID: {history_id}"
        )

    else:

        print(
            "No logged-in user found. "
            "Jewelry history not saved."
        )

    return result


# ==================================================
# HISTORY PAGE
# ==================================================

@app.get(
    "/history-page",
    response_class=HTMLResponse
)
def history_page(request: Request):

    if "user_id" not in request.session:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return templates.TemplateResponse(

        request=request,

        name="history.html"

    )


# ==================================================
# HISTORY API
# ==================================================

@app.get("/history")
def history(request: Request):

    user_id = request.session.get(
        "user_id"
    )

    if not user_id:

        return {

            "success": False,

            "message":
                "Please login first."

        }

    history_records = get_user_history(
        user_id
    )

    return {

        "success": True,

        "history":
            history_records

    }


# ==================================================
# LOGOUT
# ==================================================

@app.get("/logout")
def logout(request: Request):

    request.session.clear()

    return RedirectResponse(

        url="/login",

        status_code=303

    )