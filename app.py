import os
from datetime import datetime
from functools import wraps
from uuid import uuid4

import mysql.connector
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "change-this-secret-key")


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "root"),
        password=os.getenv("MYSQL_PASSWORD", ""),
        database=os.getenv("MYSQL_DATABASE", "maaran_cars"),
    )


def clean(value):
    return str(value or "").strip()


def registration_id(prefix):
    return f"{prefix}-{datetime.now().strftime('%Y%m%d')}-{uuid4().hex[:6].upper()}"


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            return redirect(url_for("home"))
        return view(*args, **kwargs)

    return wrapped


def format_report_period(period_value, period_format, label_format):
    if not period_value:
        return "N/A"
    try:
        if period_format == "%Y-%m":
            return datetime.strptime(str(period_value), "%Y-%m").strftime(label_format)
        return datetime.strptime(str(period_value), "%Y").strftime(label_format)
    except ValueError:
        return str(period_value)


def fetch_registration_report(period_format, label_format):
    query = """
        SELECT DATE_FORMAT(created_at, %s) AS period,
               SUM(CASE WHEN source = 'buyer' THEN 1 ELSE 0 END) AS buyer_count,
               SUM(CASE WHEN source = 'seller' THEN 1 ELSE 0 END) AS seller_count,
               COUNT(*) AS total_count
        FROM (
            SELECT created_at, 'buyer' AS source FROM buyer_registrations
            UNION ALL
            SELECT created_at, 'seller' AS source FROM seller_registrations
        ) AS combined_registrations
        GROUP BY DATE_FORMAT(created_at, %s)
        ORDER BY DATE_FORMAT(created_at, %s) ASC
    """
    params = (period_format, period_format, period_format)
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        rows = cursor.fetchall()
        for row in rows:
            row["period_label"] = format_report_period(row["period"], period_format, label_format)
            row["buyer_count"] = int(row["buyer_count"] or 0)
            row["seller_count"] = int(row["seller_count"] or 0)
            row["total_count"] = int(row["total_count"] or 0)
        return rows
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/register/buyer")
def buyer_register_page():
    return render_template("buyer_register.html", values={})


@app.get("/register/seller")
def seller_register_page():
    return render_template("seller_register.html", values={})


@app.post("/api/register/buyer")
def register_buyer():
    payload = request.form
    values = {key: clean(payload.get(key)) for key in ("phone", "name", "place", "requirement", "budget", "car_seen")}
    if not values["phone"] or not values["name"] or not values["requirement"]:
        return render_template("buyer_register.html", error="Phone number, name, and requirement are required.", values=values), 400
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO buyer_registrations
            (registration_id, phone, name, place, requirement, budget, car_seen)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (registration_id("BUY"), values["phone"], values["name"], values["place"] or None,
             values["requirement"], values["budget"] or None, values["car_seen"] or None),
        )
        connection.commit()
        return render_template("registration_success.html", registration_type="buyer"), 201
    except mysql.connector.Error:
        app.logger.exception("Database error while registering buyer")
        return render_template("buyer_register.html", error="We could not save your registration. Check MySQL and try again.", values=values), 503
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@app.post("/api/register/seller")
def register_seller():
    payload = request.form
    fields = ("name", "car_name", "car_model", "car_variant", "year", "fuel", "transmission", "ownership", "km_driven", "insurance", "place", "expecting_price", "dents", "scratches")
    values = {key: clean(payload.get(key)) for key in fields}
    if not values["name"] or not values["car_name"] or not values["car_model"]:
        return render_template("seller_register.html", error="Name, car name, and car model are required.", values=values), 400
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            """
            INSERT INTO seller_registrations
            (registration_id, name, car_name, car_model, car_variant, year, fuel,
             transmission, ownership, km_driven, insurance, place, expecting_price,
             dents, scratches)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (registration_id("SELL"), *(values[field] or None for field in fields)),
        )
        connection.commit()
        return render_template("registration_success.html", registration_type="seller"), 201
    except mysql.connector.Error:
        app.logger.exception("Database error while registering seller")
        return render_template("seller_register.html", error="We could not save your registration. Check MySQL and try again.", values=values), 503
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@app.post("/api/admin/login")
def admin_login():
    payload = request.get_json(silent=True) or request.form
    email = clean(payload.get("email")).lower()
    password = clean(payload.get("password"))

    if not email or not password:
        return jsonify({"message": "Email and password are required."}), 400

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s AND role = 'admin'", (email,))
        admin = cursor.fetchone()
        if not admin or not check_password_hash(admin["password_hash"], password):
            return jsonify({"message": "Invalid admin credentials."}), 401
        session.clear()
        session["admin_id"] = admin["id"]
        session["admin_name"] = admin["full_name"]
        return jsonify({"message": "Admin login successful.", "admin": {"name": admin["full_name"]}})
    except mysql.connector.Error:
        app.logger.exception("Database error during admin login")
        return jsonify({"message": "Admin login is temporarily unavailable."}), 503
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@app.get("/admin/dashboard")
@admin_required
def admin_dashboard():
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM buyer_registrations ORDER BY created_at DESC")
        buyers = cursor.fetchall()
        cursor.execute("SELECT * FROM seller_registrations ORDER BY created_at DESC")
        sellers = cursor.fetchall()
        return render_template("admin_dashboard.html", buyers=buyers, sellers=sellers, admin_name=session.get("admin_name"))
    except mysql.connector.Error:
        app.logger.exception("Database error loading admin dashboard")
        return render_template("admin_dashboard.html", buyers=[], sellers=[], admin_name=session.get("admin_name"), error="Registrations are unavailable. Check the MySQL connection."), 503
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@app.get("/admin/report/monthly")
@admin_required
def admin_monthly_report():
    report_rows = fetch_registration_report("%Y-%m", "%b %Y")
    total_buyers = sum(row["buyer_count"] for row in report_rows)
    total_sellers = sum(row["seller_count"] for row in report_rows)
    return render_template(
        "admin_reports.html",
        admin_name=session.get("admin_name"),
        report_title="Monthly report",
        report_type="monthly",
        report_rows=report_rows,
        total_buyers=total_buyers,
        total_sellers=total_sellers,
        total_registrations=total_buyers + total_sellers,
    )


@app.get("/admin/report/yearly")
@admin_required
def admin_yearly_report():
    report_rows = fetch_registration_report("%Y", "%Y")
    total_buyers = sum(row["buyer_count"] for row in report_rows)
    total_sellers = sum(row["seller_count"] for row in report_rows)
    return render_template(
        "admin_reports.html",
        admin_name=session.get("admin_name"),
        report_title="Yearly report",
        report_type="yearly",
        report_rows=report_rows,
        total_buyers=total_buyers,
        total_sellers=total_sellers,
        total_registrations=total_buyers + total_sellers,
    )


@app.get("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("home"))


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "maaran-cars", "time": datetime.utcnow().isoformat()})


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "1") == "1")
