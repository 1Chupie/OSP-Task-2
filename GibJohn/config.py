import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///form.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'pufta' 