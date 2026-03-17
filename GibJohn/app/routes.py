from werkzeug.security import generate_password_hash
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import Contact, Register
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index(): 
    return render_template('index.html', title="Home Page")

@main.route('/about')
def about():
    return render_template('about.html', title = 'About')

@main.route('/contact')
def contact():
    return render_template('contact.html', title = 'Contact Us')

@main.route('/testimonies')
def testimonies():
    return render_template('testimonies.html', title = 'Testimonies')

@main.route('/register')
def register():
    return render_template('register.html', title = 'Register')




@main.route('/submit_contact', methods=['POST'])
def submit():
    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    if not name or not email or not message:
        flash('All fields are required!')
        return redirect(url_for('main.contact'))

    new_contact = Contact(name=name, email=email, message=message)
    db.session.add(new_contact)
    db.session.commit()

    flash('Your message has been sent successfully!')
    return redirect(url_for('main.contact'))





@main.route('/submit_register', methods=['GET', 'POST'])
def submit_register():

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not email or not password or not confirm_password:
            flash('All fields are required!')
            return redirect(url_for('main.register'))

        if password != confirm_password:
            flash('Passwords do not match!')
            return redirect(url_for('main.register'))
    
        existing_user = Register.query.filter((Register.username == username) | (Register.email == email)).first()
        if existing_user:
            flash('Username or email already exists!', 'danger')
            return redirect(url_for('main.register'))

        hashed_password = generate_password_hash(password)
        new_register = Register(username=username, email=email, password=hashed_password, confirm_password=hashed_password)
        db.session.add(new_register)
        db.session.commit()

        flash('You have registered successfully!')
        return redirect(url_for('main.register'))

    return render_template('register.html', title='Register')

@main.route('/login', methods=['GET', 'POST'])
def login():
    #
    #

    return render_template('login.html')