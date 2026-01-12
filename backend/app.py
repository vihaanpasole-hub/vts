from flask import Flask
from backend.routes import main_routes
from backend.config import Config
from backend.models import db, User
from datetime import timedelta
from werkzeug.security import generate_password_hash
from backend.models import db, User, Quote, Product


app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static",
    instance_relative_config=True
)


# Stable secret key
app.secret_key = "vts_super_secret_key_2026"

# Session auto-expire
app.permanent_session_lifetime = timedelta(minutes=30)

# Load config
app.config.from_object(Config)

# Init DB
db.init_app(app)

# Register routes
app.register_blueprint(main_routes)

# Create tables & ensure admin
with app.app_context():
    db.create_all()

    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            password=generate_password_hash("admin123")
        )
        db.session.add(admin)
        db.session.commit()

    print("DB PATH =", app.config["SQLALCHEMY_DATABASE_URI"])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)


app = app
