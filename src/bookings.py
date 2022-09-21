import time
from datetime import datetime

from flask_login import login_required, current_user
from flask import Blueprint, render_template, redirect, url_for, request, flash
from sqlalchemy import and_

from src.auth import login

from .models import Room, User, Booking

from . import db

bookings = Blueprint('bookings', __name__)

@bookings.route('/book')
@login_required
def book_page():
    rooms = Room.query.all()

    return render_template('book.html', rooms=rooms)

@bookings.route('/book', methods=['POST'])
@login_required
def book_post():
    name = request.form.get('name')
    room_id = request.form.get('room')
    start_time = request.form.get('starttime')
    end_time = request.form.get("endtime")

    start_timestamp = datetime_to_timestamp(start_time)
    end_timestamp = datetime_to_timestamp(end_time)

    current_timestamp = int(time.time())

    if start_timestamp <= current_timestamp or end_timestamp <= current_timestamp:
        flash("Booking cannot be in the past")
        return redirect(url_for('bookings.book_page'))

    if end_timestamp < start_timestamp:
        flash("End time can not be before start time")
        return redirect(url_for('bookings.book_page'))

    # TODO
    # Check if room id is empty
    # Check if start and end timestamps are in the future int(time.time())
    # Query for bookings where room_id = room_id AND start_time > db.start_time AND start_time < db.end_time AND end_time > db.start_time
    booking = Booking.query.filter(
        and_(
            room_id == Booking.room_id,
            start_timestamp >= Booking.start_time,
            end_timestamp <= Booking.end_time,
            end_timestamp >= Booking.start_time
        )
    )

    if not booking:
        flash('Room is already booked at this time')
        return redirect(url_for('bookings.book_page'))
    

    new_booking = Booking(booking_name=name, room_id=room_id, start_time=start_timestamp, end_time=end_timestamp, user_id=current_user.id)

    # Add new room to database
    db.session.add(new_booking)
    db.session.commit()

    return redirect(url_for('bookings.bookings_page'))
    
@bookings.route('/bookings')
@login_required
def bookings_page():
    bookings = db.session.query(Booking, Room, User).join(Room, Booking.room_id == Room.id).join(User, Booking.user_id == User.id).filter(Booking.user_id == current_user.id).all()

    return render_template('bookings.html', admin_page=False, bookings=bookings, fromtimestamp=datetime.fromtimestamp)

@bookings.route('/bookings/<int:id>', methods=['POST'])
def delete_bookings(id):
    booking = Booking.query.get_or_404(id)

    db.session.delete(booking)
    db.session.commit()

    return redirect(url_for('bookings.bookings_page'))

def datetime_to_timestamp(input_string):
    return time.mktime(datetime.strptime(input_string, "%Y-%m-%dT%H:%M").timetuple())
