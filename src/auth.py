from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def login():
    return render_template('login.html')

@auth.route('/login', methods=['POST'])
def login_post():
    # User can log in with the parameters below
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # Check if the user actually exists
    # Take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('auth.login')) # If the user doesn't exist or password is wrong, reload the page

    # If the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('bookings.book_page'))

@auth.route('/signup')
def signup():
    return render_template('signup.html')

@auth.route('/signup', methods=['POST'])
def signup_post():
    # User signs up and inserts the below information
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.filter_by(email=email).first() # If this returns a user, then the email already exists in database

    if user: # If a user is found, redirect back to signup page so user can try again
        flash('Email address already exists. Use a different email or login')
        return redirect(url_for('auth.signup'))
    
    if email == "" or name == "" or password == "":
        flash('Please input all fields and try again')
        return redirect(url_for('auth.signup'))

    # Create a new user with the form data. Hash the password.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'), admin=False)

    # Add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
