from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import mongo, csrf, mail
from utils.logger import log_event, LOG_TYPES
from utils.token import generate_confirmation_token, confirm_token
from flask_mail import Message
import logging

user_bp = Blueprint("user", __name__)
logger = logging.getLogger(__name__)

@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        user = mongo.db.customers.find_one({"Email": email})
        if user and check_password_hash(user["Password"], password):
            session["customer_name"] = user["CustomerName"]
            session["customer_type"] = user["CustomerType"]
            flash("Giriş başarılı.", "success")
            log_event("login", f"{user['CustomerName']} giriş yaptı.", user["CustomerName"])
            return redirect(url_for("order.order_panel") if user["CustomerType"] == "Admin" else url_for("user.profile"))
        else:
            flash("Geçersiz email veya şifre.", "danger")
    return render_template("login.html")

@user_bp.route("/logout")
def logout():
    if session.get("customer_name"):
        log_event("logout", f"{session['customer_name']} çıkış yaptı.", session["customer_name"])
    session.clear()
    flash("Başarıyla çıkış yaptınız.", "success")
    return redirect(url_for("user.login"))

@user_bp.route("/profile", methods=["GET", "POST"])
def profile():
    if not session.get("customer_name"):
        flash("Giriş yapmalısınız.", "danger")
        return redirect(url_for("user.login"))

    cust = mongo.db.customers.find_one({"CustomerName": session["customer_name"]})
    if not cust:
        flash("Kullanıcı bulunamadı.", "danger")
        return redirect(url_for("user.login"))

    if request.method == "POST":
        data = request.form
        budget = data.get("budget", "").strip()
        if not budget.isdigit():
            return jsonify({"success": False, "message": "Geçerli bir bütçe giriniz."}), 400
        budget = float(budget)
        if budget < 0:
            return jsonify({"success": False, "message": "Bütçe negatif olamaz."}), 400

        try:
            mongo.db.customers.update_one({"CustomerName": session["customer_name"]},
                                          {"$set": {"Budget": budget}})
            log_event("budget_updated", f"Bütçe güncellendi: {budget}", cust["CustomerID"])
            return jsonify({"success": True, "message": "Bütçe başarıyla güncellendi."}), 200
        except Exception as e:
            logger.error(f"Bütçe güncelleme hatası: {e}")
            return jsonify({"success": False, "message": "Bütçe güncellenirken hata oluştu."}), 500

    return render_template("profile.html", customer=cust)

@user_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        customer_type = request.form.get("customer_type", "Standard")
        budget = request.form.get("budget", "5000").strip()

        if not name or not email or not password or not budget.isdigit():
            flash("Tüm alanları doğru doldurun.", "danger")
            return render_template("register.html")

        budget = float(budget)

        existing = mongo.db.customers.find_one({"Email": email})
        if existing:
            flash("Bu email zaten kayıtlı.", "danger")
            return render_template("register.html")

        last_c = mongo.db.customers.find_one(sort=[("CustomerID", -1)])
        next_id = last_c["CustomerID"] + 1 if last_c else 1

        new_cust = {
            "CustomerID": next_id,
            "CustomerName": name,
            "Email": email,
            "Budget": budget,
            "CustomerType": customer_type,
            "TotalSpent": 0,
            "Password": generate_password_hash(password),
            "confirmed": False,
            "confirmation_token": generate_confirmation_token(email)
        }
        try:
            mongo.db.customers.insert_one(new_cust)
            log_event(LOG_TYPES["customer_added"], f"Müşteri eklendi: {name}", "Admin")
            flash("Kayıt başarılı. E-posta ile onaylama yapmanız gerekiyor.", "success")
            return redirect(url_for("user.login"))
        except Exception as e:
            logger.error(f"Kayıt hatası: {e}")
            flash("Kayıt sırasında hata oluştu.", "danger")
            return render_template("register.html")

@user_bp.route("/confirm/<token>")
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash("Onay linki geçersiz veya süresi dolmuş.", "danger")
        return redirect(url_for("user.login"))

    user = mongo.db.customers.find_one({"Email": email})
    if not user:
        flash("Kullanıcı bulunamadı.", "danger")
        return redirect(url_for("user.login"))
    if user["confirmed"]:
        flash("Hesabınız zaten onaylanmış.", "success")
    else:
        mongo.db.customers.update_one({"Email": email}, {"$set": {"confirmed": True}})
        flash("Hesabınız onaylandı. Giriş yapabilirsiniz.", "success")
        log_event("email_confirmed", f"{user['CustomerName']} email onayladı.", user["CustomerName"])
    return redirect(url_for("user.login"))
