import os
from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from backend.models import db, User, Quote, Product


main_routes = Blueprint("main_routes", __name__)

# ---------------- ADMIN GATE (BLOCK DIRECT /admin) ----------------
@main_routes.route("/admin")
def admin_gate():
    return redirect("/login")

# ---------------- HOME ----------------
@main_routes.route("/")
def home():
    return render_template("index.html")

# ---------------- PRODUCTS PAGE ----------------
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

# ---------------- REAL ADMIN PANEL ----------------
@main_routes.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    quotes = Quote.query.all()
    products = Product.query.all()

    print("ADMIN PRODUCTS =", products)   # Render logs me dikhega

    return render_template(
        "admin.html",
        quotes=quotes,
        products=products
    )

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

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        upload_folder = os.path.join(base_dir, "static", "uploads")

        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        filename = secure_filename(file.filename)
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

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
    product = Product.query.get(id)
    return render_template("product_detail.html", p=product)

# ---------------- DELETE PRODUCT ----------------
@main_routes.route("/delete-product/<int:id>", methods=["POST"])
def delete_product(id):
    if "user" not in session:
        return redirect("/login")

    product = Product.query.get_or_404(id)

    # (optional) image file delete
    if product.image:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        upload_folder = os.path.join(base_dir, "static", "uploads")
        image_path = os.path.join(upload_folder, product.image)

        if os.path.exists(image_path):
            os.remove(image_path)

    db.session.delete(product)
    db.session.commit()

    return redirect("/dashboard")

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

            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            upload_folder = os.path.join(base_dir, "static", "uploads")

            import uuid
            ext = os.path.splitext(file.filename)[1]
            filename = str(uuid.uuid4()) + ext

            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            product.image = filename

        db.session.commit()
        return redirect("/dashboard")

    return render_template("edit_product.html", p=product)






