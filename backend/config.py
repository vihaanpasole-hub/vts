import os

SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

if not SQLALCHEMY_DATABASE_URI:
    raise RuntimeError("DATABASE_URL is not set")

SQLALCHEMY_TRACK_MODIFICATIONS = False
