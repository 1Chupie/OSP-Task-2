# 📦 OSP Task 2 Example

> A Flask-based web application with user authentication, booking management, payments, and contact handling.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-Framework-black?logo=flask)
![SQLite](https://img.shields.io/badge/Database-SQLite-lightblue?logo=sqlite)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

## 📋 Table of Contents

- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
- [Configuration](#️-configpy)
- [App Factory](#️-__init__py)
- [Database Init](#️-_init_dbpy)
- [Models](#️-modelspy)
  - [User System](#-user-system)
  - [Item System](#️-item-system)
  - [Booking System](#-booking-system)
  - [Contact System](#-contact-system)
- [Routes](#-routespy)
  - [Page Routes](#-page-routes)
  - [Authentication Routes](#-authentication-routes)
  - [Booking Routes](#-booking-routes)
  - [Payment Routes](#-payment-routes)
  - [Contact Route](#-contact-route)
- [Database Schema](#️-database-schema)
- [Security Notes](#️-security-notes)
- [Tech Stack](#-tech-stack)
- [run.py](#-runpy)


---

## 📁 Project Structure
```
OSP Task 2 Example/
├── App/
│   ├── static/
│   │   ├── css/
│   │   │   └── styles.css
│   │   ├── images/
│   │   │   └── stock1.jpg
│   │   ├── js/
│   │   │   └── script.js
│   │   └── templates/
│   │       └── index.html
│   │
│   ├── __init__.py
│   ├── models.py
│   └── routes.py
│
├── _init_db.py
├── config.py
└── run.py               
```

---

## 🚀 Getting Started
```bash

# 1. Install dependencies
pip install -r requirements.txt

# 2. Initialize the database
python _init_db.py

# 3. Run the app
python run.py
```

App runs at `http://127.0.0.1:5000`

---

## ⚙️ `config.py`
```python
import os

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///example.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "your-secret-key"
```

> ⚠️ Change `SECRET_KEY` before deploying to production.

---

## 🛠️ `__init__.py`
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    from .routes import main
    app.register_blueprint(main)
    return app
```

---

## 🗄️ `_init_db.py`
```python
from app import create_app, db

app = create_app()

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")
```

---

## 🗃️ `models.py`

### 👤 User System
```python
from . import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name     = db.Column(db.String(255), nullable=False)
    email         = db.Column(db.String(255), unique=True, nullable=False)
    phone_number  = db.Column(db.String(20), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at    = db.Column(db.DateTime)

    bookings = db.relationship('Booking', backref='user', lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"
```

### 🛏️ Item System
```python
class Room(db.Model):
    __tablename__ = 'rooms'

    id                  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_type           = db.Column(db.Enum('Deluxe Suite', 'Superior Room', name="room_types"), nullable=False)
    description         = db.Column(db.Text, nullable=False)
    price_per_night     = db.Column(db.Numeric(8, 2), nullable=False)
    max_guests          = db.Column(db.Integer, nullable=False)
    image_url           = db.Column(db.String(255), nullable=True)
    availability_status = db.Column(db.Enum('available', 'booked', name="availability_status"), default='available')

    bookings = db.relationship('Booking', backref='room', lazy=True)

    def __repr__(self):
        return f"<Room {self.room_type} - {self.id}>"
```

### 📅 Booking System
```python
class Booking(db.Model):
    __tablename__ = 'bookings'

    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id        = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    room_id        = db.Column(db.Integer, db.ForeignKey('rooms.id'), nullable=False)
    check_in_date  = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    total_price    = db.Column(db.Numeric(8, 2), nullable=False)
    payment_status = db.Column(db.Enum('pending', 'paid', 'cancelled', name="payment_status"), default='pending')
    created_at     = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Booking {self.id} - User {self.user_id} - Room {self.room_id}>"
```

### 📬 Contact System
```python
class Contact(db.Model):
    __tablename__ = 'contacts'

    id         = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name       = db.Column(db.String(255), nullable=False)
    email      = db.Column(db.String(255), nullable=False)
    message    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    status     = db.Column(db.Enum('new', 'read', 'replied', name="contact_status"), default='new')

    def __repr__(self):
        return f"<Contact {self.id} - {self.email}>"
```

---

## 🔀 `routes.py`

### 🌐 Page Routes
```python
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import Booking, User, Room, Contact
from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import calendar

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html', title="Home Page")

@main.route('/gallery')
def gallery():
    return render_template('gallery.html', title="Gallery")

@main.route('/dining')
def dining():
    return render_template('dining.html', title="Dining")

@main.route('/contacts')
def contacts():
    return render_template('contacts.html', title="Contacts")

@main.route('/location')
def location():
    return render_template('location.html', title="Location")

@main.route('/rooms')
def rooms():
    today = datetime.today()
    month = request.args.get('month', today.month, type=int)
    year = request.args.get('year', today.year, type=int)

    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdatescalendar(year, month)

    deluxe_rooms = Room.query.filter_by(room_type="Deluxe Suite").all()
    superior_rooms = Room.query.filter_by(room_type="Superior Room").all()

    availability = {}
    for week in month_days:
        for day in week:
            if day.month == month:
                deluxe_booked = Booking.query.join(Room).filter(
                    Room.room_type == "Deluxe Suite",
                    Booking.check_in_date <= day,
                    Booking.check_out_date > day
                ).count()

                superior_booked = Booking.query.join(Room).filter(
                    Room.room_type == "Superior Room",
                    Booking.check_in_date <= day,
                    Booking.check_out_date > day
                ).count()

                availability[day] = {
                    "deluxe_available": len(deluxe_rooms) - deluxe_booked,
                    "superior_available": len(superior_rooms) - superior_booked
                }

    return render_template(
        "rooms.html",
        month=month,
        year=year,
        month_days=month_days,
        availability=availability,
        calendar=calendar
    )
```

### 🔐 Authentication Routes
```python
@main.route('/login')
def login():
    return render_template('login.html', title="Login")

@main.route('/register')
def register():
    return render_template('register.html', title="Register")

@main.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('main.login'))

@main.route('/Submit_Login', methods=['GET', 'POST'])
def submit_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Both email and password are required!')
            return render_template('login.html', title='Login')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Login successful!')
            return redirect(url_for('main.booking'))
        else:
            flash('Invalid email or password!')
            return render_template('login.html', title='Login')

    return redirect(url_for('main.login'))

@main.route('/Submit_Register', methods=['GET', 'POST'])
def submit_register():
    if request.method == 'POST':
        full_name       = request.form.get('name')
        email           = request.form.get('email')
        phone_number    = request.form.get('phone')
        password        = request.form.get('password')
        verify_password = request.form.get('verify_password')

        if not full_name or not email or not phone_number or not password or not verify_password:
            flash('All fields are required!')
            return render_template('register.html', title='Register')

        if password != verify_password:
            flash('Passwords do not match!')
            return render_template('register.html', title='Register')

        new_user = User(
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            password_hash=generate_password_hash(password)
        )
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!')
        return redirect(url_for('main.index'))

    return redirect(url_for('main.register'))
```

### 📅 Booking Routes
```python
@main.route('/booking')
def booking():
    if 'user_id' not in session:
        flash('Please log in to access your account.')
        return redirect(url_for('main.login'))
    user = User.query.get(session['user_id'])
    return render_template('booking.html', title='Booking', user=user)

@main.route('/Submit_Booking', methods=['POST'])
def submit_booking():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('main.login'))

    checkin_date  = request.form.get('checkin_date')
    checkout_date = request.form.get('checkout_date')
    room_type     = request.form.get('room_type')

    if not checkin_date or not checkout_date or not room_type:
        flash('All fields are required')
        return redirect(url_for('main.booking'))

    checkin_date  = datetime.strptime(checkin_date, '%Y-%m-%d').date()
    checkout_date = datetime.strptime(checkout_date, '%Y-%m-%d').date()

    if room_type == "deluxe":
        room = Room.query.filter_by(room_type="Deluxe Suite").first()
    elif room_type == "superior":
        room = Room.query.filter_by(room_type="Superior Room").first()
    else:
        flash("Invalid room type")
        return redirect(url_for('main.booking'))

    if not room:
        flash("No available rooms of that type")
        return redirect(url_for('main.booking'))

    nights      = (checkout_date - checkin_date).days
    total_price = nights * float(room.price_per_night)

    new_booking = Booking(
        user_id=session['user_id'],
        room_id=room.id,
        check_in_date=checkin_date,
        check_out_date=checkout_date,
        total_price=total_price
    )

    db.session.add(new_booking)
    db.session.commit()
    flash("Booking successful!")
    return redirect(url_for('main.booking'))
```

### 💳 Payment Routes
```python
@main.route('/process_payment', methods=['POST'])
def process_payment():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('main.login'))

    checkin_date  = request.form.get('checkin_date')
    checkout_date = request.form.get('checkout_date')
    room_type     = request.form.get('room_type')
    cardnumber    = request.form.get('cardnumber', '').replace(' ', '')
    expiry        = request.form.get('expiry', '')
    cvv           = request.form.get('cvv', '')

    if not cardnumber or len(cardnumber) != 16 or not cardnumber.isdigit():
        flash('Card number must be 16 digits')
        return redirect(url_for('main.booking'))

    if not expiry or '/' not in expiry:
        flash('Invalid expiry date format')
        return redirect(url_for('main.booking'))

    if not cvv or not cvv.isdigit() or len(cvv) < 3 or len(cvv) > 4:
        flash('CVV must be 3-4 digits')
        return redirect(url_for('main.booking'))

    try:
        checkin_date  = datetime.strptime(checkin_date, '%Y-%m-%d').date()
        checkout_date = datetime.strptime(checkout_date, '%Y-%m-%d').date()

        if room_type == "deluxe":
            room = Room.query.filter_by(room_type="Deluxe Suite").first()
        elif room_type == "superior":
            room = Room.query.filter_by(room_type="Superior Room").first()
        else:
            flash("Invalid room type")
            return redirect(url_for('main.booking'))

        if not room:
            flash("No available rooms of that type")
            return redirect(url_for('main.booking'))

        nights      = (checkout_date - checkin_date).days
        total_price = nights * float(room.price_per_night)

        new_booking = Booking(
            user_id=session['user_id'],
            room_id=room.id,
            check_in_date=checkin_date,
            check_out_date=checkout_date,
            total_price=total_price,
            payment_status='paid'
        )

        db.session.add(new_booking)
        db.session.commit()

        flash("Booking successful! Payment confirmed.")
        return redirect(url_for('main.booking'))

    except Exception as e:
        flash(f"Booking failed: {str(e)}")
        return redirect(url_for('main.booking'))

@main.route('/process_pending_payment', methods=['POST'])
def process_pending_payment():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('main.login'))

    booking_id = request.form.get('booking_id')
    cardnumber = request.form.get('cardnumber', '').replace(' ', '')
    expiry     = request.form.get('expiry', '')
    cvv        = request.form.get('cvv', '')

    if not cardnumber or len(cardnumber) != 16 or not cardnumber.isdigit():
        flash('Card number must be 16 digits')
        return redirect(url_for('main.booking'))

    if not expiry or '/' not in expiry:
        flash('Invalid expiry date format')
        return redirect(url_for('main.booking'))

    if not cvv or not cvv.isdigit() or len(cvv) < 3 or len(cvv) > 4:
        flash('CVV must be 3-4 digits')
        return redirect(url_for('main.booking'))

    booking = Booking.query.get(booking_id)

    if not booking or booking.user_id != session['user_id']:
        flash('Booking not found or unauthorized')
        return redirect(url_for('main.booking'))

    if booking.payment_status == 'paid':
        flash('This booking is already paid')
        return redirect(url_for('main.booking'))

    booking.payment_status = 'paid'
    db.session.commit()

    flash('Payment successful!')
    return redirect(url_for('main.booking'))
```

### 📬 Contact Route
```python
@main.route('/submit_contact', methods=['POST'])
def submit_contact():
    name    = request.form.get('name')
    email   = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        flash('All fields are required')
        return redirect(url_for('main.contacts'))

    new_contact = Contact(
        name=name,
        email=email,
        message=message,
        created_at=datetime.now()
    )

    db.session.add(new_contact)
    db.session.commit()

    flash('Your message has been sent successfully!')
    return redirect(url_for('main.contacts'))
```

---

## 🗺️ Database Schema
```
users                        bookings
─────────────────────        ──────────────────────
id          (PK)             id             (PK)
full_name                    user_id        (FK → users.id)
email                        room_id        (FK → rooms.id)
phone_number                 check_in_date
password_hash                check_out_date
created_at                   total_price
                             payment_status (pending/paid/cancelled)
rooms                        created_at
─────────────────────
id          (PK)             contacts
room_type                    ──────────────────────
description                  id             (PK)
price_per_night              name
max_guests                   email
image_url                    message
availability_status          created_at
                             status         (new/read/replied)
```

---

## 🛡️ Security Notes

- Passwords hashed with `werkzeug.security.generate_password_hash`
- Auth-protected routes check `session['user_id']` before proceeding
- Basic server-side card validation (format only — no real payment gateway)

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python / Flask |
| Database | SQLite / SQLAlchemy |
| Auth | Werkzeug + Flask sessions |
| Frontend | HTML, CSS, JavaScript |
| Templating | Jinja2 |

---

## 🚀 `run.py`
```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```
