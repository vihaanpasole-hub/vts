import os
from backend.models import db


class Config:
    SECRET_KEY = "vts_secret_123"
    SQLALCHEMY_DATABASE_URI = "sqlite:///instance/database.db"


    SQLALCHEMY_TRACK_MODIFICATIONS = False
