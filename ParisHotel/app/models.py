from . import db
from datetime import datetime


# User Model
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    phone_number = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime)

    # Relationship: One user can have multiple bookings
    bookings = db.relationship('Booking', backref='user', lazy=True)


    def __repr__(self):
        return f"<User {self.email}>"


# Room Model
class Room(db.Model):
    __tablename__ = 'rooms'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_type = db.Column(db.Enum('Deluxe Suite', 'Superior Room', name="room_types"), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price_per_night = db.Column(db.Numeric(8, 2), nullable=False)
    max_guests = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    availability_status = db.Column(db.Enum('available', 'booked', name="availability_status"), default='available')

    # Relationship: One room can have multiple bookings
    bookings = db.relationship('Booking', backref='room', lazy=True)

    def __repr__(self):
        return f"<Room {self.room_type} - {self.id}>"


# Booking Model
class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    total_price = db.Column(db.Numeric(8, 2), nullable=False)
    payment_status = db.Column(db.Enum('pending', 'paid', 'cancelled', name="payment_status"), default='pending')
    created_at = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Booking {self.id} - User {self.user_id} - Room {self.room_id}>"
    

class Contact(db.Model):
    __tablename__ = 'contacts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    status = db.Column(db.Enum('new', 'read', 'replied', name="contact_status"), default='new')

    def __repr__(self):
        return f"<Contact {self.id} - {self.email}>"