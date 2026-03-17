import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  # You can change this to any other SQL database URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "mysecretpassword"
   