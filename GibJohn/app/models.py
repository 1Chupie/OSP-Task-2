from . import db

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    message = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Contact(' {self.name}'', '{self.email}'')"
    
class Register(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    confirm_password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"Register(' {self.username}'', '{self.email}'')"