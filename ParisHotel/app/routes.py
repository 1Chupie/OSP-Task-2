from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import Booking, User, Room, Contact
from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import calendar
from sqlalchemy import and_

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

@main.route('/booking')
def booking():
    if 'user_id' not in session:
        flash('Please log in to access your account.')
        return redirect(url_for('main.login'))
    user = User.query.get(session['user_id'])

    return render_template('booking.html', title='Booking', user=user)


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

@main.route('/Submit_Booking', methods=['POST'])
def submit_booking():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('main.login'))

    checkin_date = request.form.get('checkin_date')
    checkout_date = request.form.get('checkout_date')
    room_type = request.form.get('room_type')

    if not checkin_date or not checkout_date or not room_type:
        flash('All fields are required')
        return redirect(url_for('main.booking'))

    checkin_date = datetime.strptime(checkin_date, '%Y-%m-%d').date()
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

    nights = (checkout_date - checkin_date).days
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
        full_name = request.form.get('name')
        email = request.form.get('email')
        phone_number = request.form.get('phone')
        password = request.form.get('password')
        verify_password = request.form.get('verify_password')

        if not full_name or not email or not phone_number or not password or not verify_password:
            flash('All fields are required!')
            return render_template('register.html', title='Register')

        if password != verify_password:
            flash('Passwords do not match!')
            return render_template('register.html', title='Register')

        new_user = User(full_name=full_name, email=email, phone_number=phone_number, password_hash=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful!')
        return redirect(url_for('main.index'))

    return redirect(url_for('main.register'))


@main.route('/submit_contact', methods=['POST'])
def submit_contact():
    name = request.form.get('name')
    email = request.form.get('email')
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


@main.route('/process_payment', methods=['POST'])
def process_payment():
    if 'user_id' not in session:
        flash('Please log in first.')
        return redirect(url_for('main.login'))

    checkin_date = request.form.get('checkin_date')
    checkout_date = request.form.get('checkout_date')
    room_type = request.form.get('room_type')
    cardnumber = request.form.get('cardnumber', '').replace(' ', '')
    expiry = request.form.get('expiry', '')
    cvv = request.form.get('cvv', '')

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
        checkin_date = datetime.strptime(checkin_date, '%Y-%m-%d').date()
        checkout_date = datetime.strptime(checkout_date, '%Y-%m-%d').date()

        if room_type == "deluxe":
            room = Room.query.filter_by(room_type="Deluxe Suite").first()
        elif room_type == "superior":
            Room.query.filter_by(room_type="Superior Room").first()
        else:
            flash("Invalid room type")
            return redirect(url_for('main.booking'))

        if not room:
            flash("No available rooms of that type")
            return redirect(url_for('main.booking'))

        nights = (checkout_date - checkin_date).days
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
    expiry = request.form.get('expiry', '')
    cvv = request.form.get('cvv', '')

    # Basic validation
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

    # Update payment status to paid
    booking.payment_status = 'paid'
    db.session.commit()

    flash('Payment successful!')
    return redirect(url_for('main.booking'))