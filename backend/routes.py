import os
import uuid
from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import check_password_hash
from backend.models import db, User, Quote, Product
from supabase import create_client

# ---------------- SUPABASE ----------------
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("SUPABASE_URL or SUPABASE_KEY is missing in Render Environment Variables")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

main_routes = Blueprint("main_routes", __name__)

# ---------------- ADMIN GATE ----------------
@main_routes.route("/admin")
def admin_gate():
    return redirect("/login")

# ---------------- HOME ----------------
@main_routes.route("/")
def home():
    return render_template("index.html")

# ---------------- PRODUCTS ----------------
@main_routes.route("/products-page")
def products_page():
    return render_template("products.html")

# ---------------- API ----------------
@main_routes.route("/api/products")
def api_products():
    products = Product.query.all()
    return {
        "products": [
            {
                "id": p.id,
                "brand": p.brand,
                "name": p.name,
                "description": p.description,
                "image": p.image
            } for p in products
        ]
    }

# ---------------- LOGIN ----------------
@main_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form.get("username")).first()
        if user and check_password_hash(user.password, request.form.get("password")):
            session.clear()
            session["user"] = user.username
            return redirect("/dashboard")
    return render_template("login.html")

# ---------------- DASHBOARD ----------------
@main_routes.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    quotes = Quote.query.all()
    products = Product.query.all()
    return render_template("admin.html", quotes=quotes, products=products)

# ---------------- LOGOUT ----------------
@main_routes.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------- ADD PRODUCT ----------------
@main_routes.route("/add-product", methods=["GET", "POST"])
def add_product():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        file = request.files["image"]

        ext = os.path.splitext(file.filename)[1]
        filename = str(uuid.uuid4()) + ext

        supabase.storage.from_("product-images").upload(
            filename,
            file.read(),
            {"content-type": file.content_type}
        )

        p = Product(
            brand=request.form["brand"],
            name=request.form["name"],
            description=request.form["description"],
            image=filename
        )

        db.session.add(p)
        db.session.commit()
        return redirect("/dashboard")

    return render_template("add_product.html")

# ---------------- EDIT PRODUCT ----------------
@main_routes.route("/edit-product/<int:id>", methods=["GET", "POST"])
def edit_product(id):
    if "user" not in session:
        return redirect("/login")

    product = Product.query.get_or_404(id)

    if request.method == "POST":
        product.brand = request.form["brand"]
        product.name = request.form["name"]
        product.description = request.form["description"]

        if "image" in request.files and request.files["image"].filename != "":
            file = request.files["image"]
            ext = os.path.splitext(file.filename)[1]
            filename = str(uuid.uuid4()) + ext

            supabase.storage.from_("product-images").upload(
                filename,
                file.read(),
                {"content-type": file.content_type}
            )

            product.image = filename

        db.session.commit()
        return redirect("/dashboard")

    return render_template("edit_product.html", p=product)

# ---------------- DELETE PRODUCT ----------------
@main_routes.route("/delete-product/<int:id>", methods=["POST"])
def delete_product(id):
    if "user" not in session:
        return redirect("/login")

    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect("/dashboard")

# ---------------- QUOTE ----------------
@main_routes.route("/quote", methods=["GET", "POST"])
def quote():
    if request.method == "POST":
        q = Quote(
            name=request.form["name"],
            phone=request.form["phone"],
            message=request.form["message"]
        )
        db.session.add(q)
        db.session.commit()
        return redirect("/")
    return render_template("quote.html")


# ---------------- PRODUCT DETAIL ----------------
@main_routes.route("/product/<int:id>")
def product_detail(id):
    product = Product.query.get_or_404(id)

    # IMAGE URL BUILD (SINGLE SOURCE OF TRUTH)
    if product.image and product.image.startswith("http"):
        image_url = product.image
    else:
        image_url = (
            f"{SUPABASE_URL}/storage/v1/object/public/"
            f"product-images/{product.image}"
        )

    return render_template(
        "product_detail.html",
        p=product,
        image_url=image_url
    )
