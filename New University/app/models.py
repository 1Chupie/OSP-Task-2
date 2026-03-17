from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(10), default='student')  # 'student' or 'admin'
    
    # Relationships
    clubs_created = db.relationship('Club', backref='owner', foreign_keys='Club.owner_id')
    memberships = db.relationship('Membership', backref='user', foreign_keys='Membership.user_id')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to Memberships
    members = db.relationship('Membership', backref='club', foreign_keys='Membership.club_id')

    def __repr__(self):
        return f"<Club {self.name}, Owner: {self.owner.username}>"


class Membership(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey('club.id'), nullable=False)
    joined_on = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Membership User: {self.user.username}, Club: {self.club.name}>"