# routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from __init__ import app, db
from python.models import User, Doctor, Appointment, Feedback
from python.forms import LoginForm, SignupForm, AppointmentForm
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/main')
def main():
    return render_template('main.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main'))
        else:
            flash('Login failed. Check your username and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/patient-signup', methods=['GET', 'POST'])
def patient_signup():
    form = SignupForm()
    if form.validate_on_submit():
        # print("Form validated successfully")  # Debugging statement
        # try:
            hashed_password = generate_password_hash(form.password.data)
            new_user = User(username=form.username.data, password=hashed_password, role='patient')
            db.session.add(new_user)
            db.session.commit()
            # print("User  added to the database")  # Debugging statement
            flash('Patient signup successful! You can now log in.', 'success')
            return redirect(url_for('login'))
    else:
        flash('Please correct the errors in the form.', 'danger')
        # except Exception as e:
        #     db.session.rollback()  # Rollback the session in case of error
        #     # print(f'Error occurred: {str(e)}')  # Debugging statement
        #     flash(f'Error occurred: {str(e)}', 'danger')
    return render_template('patient_signup.html', form=form)

@app.route('/doctor-signup', methods=['GET', 'POST'])
def doctor_signup():
    form = SignupForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, password=form.password.data, role='doctor')
        db.session.add(new_user)
        db.session.commit()
        flash('Doctor signup successful! You can now log in.', 'success')
        return redirect(url_for('login'))  # Redirect to the login page
    return render_template('doctor_signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    appointments = Appointment.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', appointments=appointments)

@app.route('/create_appointment', methods=['POST'])
@login_required
def create_appointment():
    doctor_id = request.form['doctor']
    date = request.form['date']
    time = request.form['time']
    
    new_appointment = Appointment(user_id=current_user.id, doctor_id=doctor_id, appointment_date=date, appointment_time=time)
    db.session.add(new_appointment)
    db.session.commit()
    
    flash('Appointment created successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/cancel_appointment/<int:appointment_id>')
@login_required
def cancel_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    if appointment.user_id == current_user.id:
        db.session.delete(appointment)
        db.session.commit()
        flash('Appointment canceled successfully!', 'success')
    else:
        flash('You do not have permission to cancel this appointment.', 'danger')
    return redirect(url_for('dashboard'))

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        
        new_feedback = Feedback(name=name, email=email, message=message)
        db.session.add(new_feedback)
        db.session.commit()
        
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('feedback'))
    
    return render_template('feedback.html')

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/list_of_doctors', methods=['GET'])
def list_of_doctors():
    doctors = Doctor.query.all()
    return render_template('list_of_doctors.html', doctors=doctors)

@app.route('/membership_plans')
def membership_plans():
    return render_template('membership_plans.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))