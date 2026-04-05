import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from supabase_client import (
    sign_up, sign_in, sign_out, get_destinations, get_destination_by_id, 
    create_booking, get_user_bookings, get_all_bookings,
    add_destination, update_destination, delete_destination,
    get_user_profile
)
from dotenv import load_dotenv

load_dotenv()

base_dir = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(base_dir, 'templates'), static_folder=os.path.join(base_dir, 'static'))
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-secret-key")

# --- Middlewares ---

def get_current_user():
    return session.get("user")

def is_admin():
    user = get_current_user()
    if not user:
        return False
    try:
        profile = get_user_profile(user["id"]).data
        return profile.get("role") == "admin"
    except Exception:
        return False

# --- Routes ---

@app.route("/")
def index():
    destinations = get_destinations().data
    return render_template("index.html", destinations=destinations[:3])

@app.route("/destinations")
def destinations_list():
    destinations = get_destinations().data
    return render_template("destinations.html", destinations=destinations)

@app.route("/destination/<int:id>")
def destination_detail(id):
    try:
        res = get_destination_by_id(id)
        destination = res.data
        return render_template("destination_detail.html", destination=destination)
    except Exception as e:
        flash(f"Error fetching destination: {str(e)}", "danger")
        return redirect(url_for("destinations_list"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        full_name = request.form.get("full_name")
        
        try:
            res = sign_up(email, password, full_name)
            if res.user:
                flash("Registration successful! Please check your email for confirmation (if enabled) or login.", "success")
                return redirect(url_for("login"))
            else:
                flash("Signup failed. Check details.", "danger")
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
            
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        
        try:
            res = sign_in(email, password)
            if res.user:
                session["user"] = {
                    "id": res.user.id,
                    "email": res.user.email,
                    "full_name": res.user.user_metadata.get("full_name")
                }
                flash("Login successful!", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid credentials.", "danger")
        except Exception as e:
            flash(f"Login Error: {str(e)}", "danger")
            
    return render_template("login.html")

@app.route("/logout")
def logout():
    sign_out()
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))

@app.route("/dashboard")
def dashboard():
    user = get_current_user()
    if not user:
        flash("Please login to access your dashboard.", "warning")
        return redirect(url_for("login"))
    
    try:
        bookings = get_user_bookings(user["id"]).data
        profile = get_user_profile(user["id"]).data
        return render_template("dashboard.html", user=user, profile=profile, bookings=bookings)
    except Exception as e:
        flash(f"Error loading dashboard: {str(e)}", "danger")
        return redirect(url_for("index"))

@app.route("/book/<int:dest_id>", methods=["GET", "POST"])
def booking(dest_id):
    user = get_current_user()
    if not user:
        flash("Please login to book a destination.", "warning")
        return redirect(url_for("login"))
    
    dest = get_destination_by_id(dest_id).data
    
    if request.method == "POST":
        check_in = request.form.get("check_in")
        check_out = request.form.get("check_out")
        travelers = int(request.form.get("travelers"))
        total_price = float(dest["price"]) * travelers
        
        try:
            create_booking(user["id"], dest_id, check_in, check_out, travelers, total_price)
            flash("Booking successful! Check your dashboard for status.", "success")
            return redirect(url_for("dashboard"))
        except Exception as e:
            flash(f"Booking Error: {str(e)}", "danger")
            
    return render_template("booking.html", destination=dest)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if not is_admin():
        flash("Unauthorized access. Admin only.", "danger")
        return redirect(url_for("index"))
    
    if request.method == "POST":
        action = request.form.get("action")
        try:
            if action == "add":
                add_destination(
                    request.form.get("title"),
                    request.form.get("description"),
                    request.form.get("location"),
                    float(request.form.get("price")),
                    request.form.get("image_url")
                )
                flash("Destination added!", "success")
            elif action == "edit":
                update_destination(
                    request.form.get("id"),
                    request.form.get("title"),
                    request.form.get("description"),
                    request.form.get("location"),
                    float(request.form.get("price")),
                    request.form.get("image_url")
                )
                flash("Destination updated!", "success")
            elif action == "delete":
                delete_destination(request.form.get("id"))
                flash("Destination deleted!", "success")
        except Exception as e:
            flash(f"Admin Error: {str(e)}", "danger")
            
    destinations = get_destinations().data
    bookings = get_all_bookings().data
    return render_template("admin.html", destinations=destinations, bookings=bookings)

if __name__ == "__main__":
    app.run(debug=True)
