import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from supabase_client import (
    sign_up, sign_in, sign_out, get_destinations, get_destination_by_id,
    create_booking, get_user_bookings, get_all_bookings,
    add_destination, update_destination, delete_destination,
    get_user_profile, get_all_users, update_user_role, reset_password_email
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




@app.context_processor
def inject_admin():
    return dict(is_admin=is_admin)

# --- Routes ---

@app.route("/")
def index():
    destinations = get_destinations().data
    if isinstance(destinations, list):
        dest_list = destinations[:3]
    else:
        print("Error from Supabase:", destinations)
        dest_list = []
    return render_template("index.html", destinations=dest_list)

@app.route("/destinations")
def destinations_list():
    destinations = get_destinations().data
    if not isinstance(destinations, list):
        print("Error from Supabase:", destinations)
        destinations = []
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

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    user = get_current_user()
    if not user:
        flash("Please login to access your dashboard.", "warning")
        return redirect(url_for("login"))
    
    try:
        # Handle Admin Actions
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
                elif action == "update_user_role":
                    update_user_role(request.form.get("user_id"), request.form.get("role"))
                    flash("User role updated!", "success")
                
                return redirect(url_for("dashboard"))
            except Exception as e:
                flash(f"Admin Error: {str(e)}", "danger")
                return redirect(url_for("dashboard"))
                
        # Admin-specific data
        admin_data = {}
        if True:
            destinations = get_destinations().data
            if not isinstance(destinations, list): destinations = []
                
            all_bookings = get_all_bookings().data
            if not isinstance(all_bookings, list): all_bookings = []
                
            users = get_all_users().data
            if not isinstance(users, list): users = []

            stats = {
                "total_destinations": len(destinations),
                "total_users": len(users),
                "total_bookings": len(all_bookings),
                "total_revenue": sum(float(b.get("total_price", 0)) for b in all_bookings)
            }

            # ── Chart 1: Bookings per Destination ──────────────────────────
            # Seed all destinations with 0 bookings, then add real counts
            dest_counts = {d["title"]: 0 for d in destinations}
            for b in all_bookings:
                dest_dict = b.get("destinations")
                if isinstance(dest_dict, dict):
                    dest_title = dest_dict.get("title", "Unknown")
                    dest_counts[dest_title] = dest_counts.get(dest_title, 0) + 1
            # Only include destinations that have ≥1 booking (if any bookings exist)
            # But if no bookings at all, show all destinations with 0 to indicate real data
            if all_bookings:
                dest_counts = {k: v for k, v in dest_counts.items() if v > 0}
            chart_bookings = {
                "labels": list(dest_counts.keys()),
                "data":   list(dest_counts.values())
            }

            # ── Chart 2: Revenue by Location ────────────────────────────────
            # Seed all unique locations with 0 revenue
            loc_revenue = {d["location"]: 0.0 for d in destinations}
            for b in all_bookings:
                dest_dict = b.get("destinations")
                if isinstance(dest_dict, dict):
                    loc = dest_dict.get("location", "Unknown")
                    rev = float(b.get("total_price", 0))
                    loc_revenue[loc] = loc_revenue.get(loc, 0.0) + rev
            if all_bookings:
                loc_revenue = {k: v for k, v in loc_revenue.items() if v > 0}
            chart_revenue = {
                "labels": list(loc_revenue.keys()),
                "data":   list(loc_revenue.values())
            }

            # ── Chart 3: Booking Activity (Monthly) ─────────────────────────
            # Always use real data — no dummy fallback
            monthly_data = {}
            for b in all_bookings:
                try:
                    date_str = b.get("check_in") or b.get("created_at", "")
                    if date_str:
                        month = date_str[:7]   # "YYYY-MM"
                        monthly_data[month] = monthly_data.get(month, 0) + 1
                except Exception:
                    pass
            sorted_months = sorted(monthly_data.keys())
            chart_trend = {
                "labels": sorted_months,
                "data":   [monthly_data[m] for m in sorted_months]
            }
                
            admin_data = {
                "destinations": destinations,
                "all_bookings": all_bookings,
                "users": users,
                "stats": stats,
                "chart_bookings": chart_bookings,
                "chart_revenue": chart_revenue,
                "chart_trend": chart_trend
            }

        return render_template("admin.html", user=user, **admin_data)
        
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



@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if not email:
            flash("Please enter your email address.", "warning")
            return redirect(url_for("forgot_password"))
        try:
            reset_password_email(email)
            flash("If that email exists, a password reset link has been sent. Check your inbox.", "success")
            return redirect(url_for("login"))
        except Exception as e:
            flash(f"Error: {str(e)}", "danger")
    return render_template("forgot_password.html")


if __name__ == "__main__":
    app.run(debug=True)

def handler(request):
    return app