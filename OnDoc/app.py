from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime

app = Flask(__name__)

# Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(os.path.abspath(os.path.dirname(__file__)), "website.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"

# Models
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'admin', 'doctor', 'patient'
    gender = db.Column(db.String(10))
    date_of_birth = db.Column(db.Date)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialize database and create admin user
with app.app_context():
    db.create_all()
    if not User.query.filter_by(role="admin").first():
        admin = User(full_name="Admin", email="admin@ondoc.com", mobile="1234567890", role="admin")
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()

# Routes
@app.route("/")
def index():
    return render_template("landing.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form.get("email")).first()
        if user and user.check_password(request.form.get("password")):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for('admin_dashboard' if user.role == 'admin' else 'main'))
        flash("Invalid credentials!", "danger")
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        if User.query.filter_by(email=request.form.get("email")).first():
            return jsonify({"status": "error", "message": "Email already registered!"}), 409
        
        new_user = User(
            full_name=request.form.get("full_name"),
            email=request.form.get("email"),
            mobile=request.form.get("mobile"),
            role=request.form.get("role", "patient"),
            gender=request.form.get("gender"),
            date_of_birth=datetime.strptime(request.form.get("date_of_birth"), '%Y-%m-%d')
        )
        new_user.set_password(request.form.get("password"))

        db.session.add(new_user)
        db.session.commit()

        return jsonify({"status": "success", "message": "Registration successful!"})
    
    return render_template("signup.html")

@app.route("/main")
@login_required
def main():
    return render_template("main.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully!", "success")
    return redirect(url_for("index"))

@app.route("/aboutus")
def aboutus():
    return render_template("aboutus.html")

@app.route("/appointment_booking")
@login_required
def appointment_booking():
    return render_template("appointment_booking.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", user=current_user)

@app.route("/feedback")
def feedback():
    return render_template("feedback.html")

@app.route("/list_of_doctors")
def list_of_doctors():
    return render_template("list_of_doctors.html")

@app.route("/membership_plans")
def membership_plans():
    return render_template("membership_plans.html")

def get_dashboard_stats():
    total_users = User.query.count()
    total_doctors = User.query.filter_by(role='doctor').count()
    total_patients = User.query.filter_by(role='patient').count()
    
    return {
        'total_users': total_users,
        'total_doctors': total_doctors,
        'total_patients': total_patients
    }

def get_all_users():
    return User.query.order_by(User.id.desc()).all()

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.role != "admin":
        return redirect(url_for("main"))
    
    stats = get_dashboard_stats()
    users = get_all_users()
    return render_template('admin_dashboard.html', 
                         total_users=stats['total_users'],
                         total_doctors=stats['total_doctors'],
                         total_patients=stats['total_patients'],
                         users=users)

@app.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.full_name = request.form['full_name']
        user.email = request.form['email']
        user.mobile = request.form['mobile']
        user.role = request.form['role']
        user.gender = request.form['gender']
        user.date_of_birth = datetime.strptime(request.form['date_of_birth'], '%Y-%m-%d')
        
        db.session.commit()
        flash("User  updated successfully!", "success")
        return redirect(url_for('admin_dashboard'))
    
    return render_template('edit_user.html', user=user)

@app.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("User  deleted successfully!", "success")
    return redirect(url_for('admin_dashboard'))

if __name__ == "__main__":
    app.run(debug=True)