# app/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from .models import User, Club, Membership
from . import db

main = Blueprint('main', __name__)

# ---------------------------
# HOME PAGE
# ---------------------------
@main.route('/')
def index():
    clubs = Club.query.all()
    return render_template('index.html', clubs=clubs)

# ---------------------------
# STUDENT REGISTER
# ---------------------------
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for('main.register'))

        new_user = User(username=username, email=email, role='student')
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Account created! Please log in.", "success")
        return redirect(url_for('main.student_login'))

    return render_template('register.html')

# ---------------------------
# ADMIN REGISTER
# ---------------------------
@main.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email = request.form['email'].strip()
        password = request.form['password']
        admin_key = request.form.get('admin_key', '').strip()
        
        ADMIN_KEY = 'admin2026'  
        if admin_key != ADMIN_KEY:
            flash("Invalid admin registration key!", "danger")
            return redirect(url_for('main.admin_register'))

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for('main.admin_register'))

        new_admin = User(username=username, email=email, role='admin')
        new_admin.set_password(password)
        db.session.add(new_admin)
        db.session.commit()

        flash("Admin account created! Please log in.", "success")
        return redirect(url_for('main.admin_login'))

    return render_template('admin_register.html')

# ---------------------------
# STUDENT LOGIN
# ---------------------------
@main.route('/student_login', methods=['GET', 'POST'])
def student_login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        user = User.query.filter_by(email=email, role='student').first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['username'] = user.username
            session['role'] = user.role
            flash("Logged in successfully!", "success")
            return redirect(url_for('main.account'))
        else:
            flash("Invalid email or password!", "danger")
            return redirect(url_for('main.student_login'))

    return render_template('student_login.html')

# ---------------------------
# ADMIN LOGIN
# ---------------------------
@main.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email'].strip()
        password = request.form['password']

        user = User.query.filter_by(email=email, role='admin').first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_email'] = user.email
            session['username'] = user.username
            session['role'] = user.role
            flash("Admin logged in successfully!", "success")
            return redirect(url_for('main.account'))
        else:
            flash("Invalid admin credentials!", "danger")
            return redirect(url_for('main.admin_login'))

    return render_template('admin_login.html')

# ---------------------------
# ACCOUNT / DASHBOARD
# ---------------------------
@main.route('/account')
def account():
    if 'user_id' not in session:
        flash("Please log in first!", "danger")
        return redirect(url_for('main.student_login'))

    user_id = session['user_id']
    user = User.query.get(user_id)
    
    if session.get('role') == 'student':
        # Show clubs the student has joined
        memberships = Membership.query.filter_by(user_id=user_id).all()
        return render_template('account.html', memberships=memberships, user=user, role='student')
    else:  # admin
        # Show students who joined their clubs
        created_clubs = Club.query.filter_by(owner_id=user_id).all()
        return render_template('account.html', created_clubs=created_clubs, user=user, role='admin')

# ---------------------------
# JOIN CLUB
# ---------------------------
@main.route('/join/<int:club_id>')
def join_club(club_id):
    if 'user_id' not in session:
        flash("Please log in first!", "danger")
        return redirect(url_for('main.student_login'))

    user_id = session['user_id']
    
    # Check if club exists
    club = Club.query.get(club_id)
    if not club:
        flash("Club not found!", "danger")
        return redirect(url_for('main.index'))

    # Prevent duplicate membership
    if Membership.query.filter_by(user_id=user_id, club_id=club_id).first():
        flash("You are already a member of this club!", "info")
        return redirect(url_for('main.index'))

    membership = Membership(user_id=user_id, club_id=club_id)
    db.session.add(membership)
    db.session.commit()

    flash(f"Joined {club.name} successfully!", "success")
    return redirect(url_for('main.account'))

# ---------------------------
# LOGOUT
# ---------------------------
@main.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for('main.index'))

# ---------------------------
# CREATE CLUB (ADMIN ONLY)
# ---------------------------
@main.route('/create_club', methods=['GET', 'POST'])
def create_club():
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Admin access required!", "danger")
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        club_name = request.form['club_name'].strip()
        description = request.form.get('description', '').strip()
        owner_id = session['user_id']
        
        # Check if club already exists
        if Club.query.filter_by(name=club_name).first():
            flash("Club already exists!", "danger")
            return redirect(url_for('main.create_club'))
        
        new_club = Club(name=club_name, description=description, owner_id=owner_id)
        db.session.add(new_club)
        db.session.commit()
        
        flash(f"Club '{club_name}' created successfully!", "success")
        return redirect(url_for('main.account'))
    
    return render_template('create_club.html')

# ---------------------------
# VIEW CLUB DETAILS (DYNAMIC PAGE FOR ALL USERS)
# ---------------------------
@main.route('/club/<int:club_id>')
def view_club(club_id):
    club = Club.query.get(club_id)
    if not club:
        flash("Club not found!", "danger")
        return redirect(url_for('main.index'))
    
    # Get all members of this club
    members = Membership.query.filter_by(club_id=club_id).all()
    member_count = len(members)
    
    # Check if current user is a member
    is_member = False
    if 'user_id' in session:
        is_member = Membership.query.filter_by(user_id=session['user_id'], club_id=club_id).first() is not None
    
    return render_template('view_club.html', club=club, members=members, member_count=member_count, is_member=is_member)

# ---------------------------
# VIEW CLUB MEMBERS (ADMIN ONLY)
# ---------------------------
@main.route('/club/<int:club_id>/members')
def club_members(club_id):
    if 'user_id' not in session or session.get('role') != 'admin':
        flash("Admin access required!", "danger")
        return redirect(url_for('main.index'))
    
    club = Club.query.get(club_id)
    if not club or club.owner_id != session['user_id']:
        flash("Unauthorized access!", "danger")
        return redirect(url_for('main.account'))
    
    members = Membership.query.filter_by(club_id=club_id).all()
    return render_template('club_members.html', club=club, members=members)