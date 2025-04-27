from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from extensions import mongo, mail
from werkzeug.security import generate_password_hash, check_password_hash
from utils.logger import log_event
from utils.token import generate_confirmation_token, confirm_token
from utils.log_models import generate_id
from flask_mail import Message
import pyotp
import logging

user_bp = Blueprint("user", __name__)
logger = logging.getLogger(__name__)

@user_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        customer_type = request.form.get("customer_type", "Standard")
        budget_str = request.form.get("budget", "5000").strip()
        try:
            budget = float(budget_str)
        except ValueError:
            flash("Geçerli bütçe giriniz.", "danger")
            return render_template("register.html")
        existing = mongo.db.customers.find_one({"Email": email})
        if existing:
            flash("Bu email zaten kayıtlı.", "danger")
            return render_template("register.html")
        customer_id = generate_id("C")
        new_customer = {
            "CustomerID": customer_id,
            "CustomerName": name,
            "Email": email,
            "Budget": budget,
            "CustomerType": customer_type,
            "TotalSpent": 0,
            "Password": generate_password_hash(password),
            "confirmed": False,
            "confirmation_token": generate_confirmation_token(email)
        }
        if request.form.get("enable_2fa"):
            secret = pyotp.random_base32()
            new_customer["2fa_enabled"] = True
            new_customer["2fa_secret"] = secret
        else:
            new_customer["2fa_enabled"] = False
            new_customer["2fa_secret"] = None

        try:
            mongo.db.customers.insert_one(new_customer)
            confirm_url = url_for("user.activate", token=new_customer["confirmation_token"], _external=True)
            msg = Message("Email Doğrulama", recipients=[email])
            msg.html = render_template("activate.html", confirm_url=confirm_url)
            mail.send(msg)
            log_event("customer_added", f"Müşteri eklendi: {name}", "Admin", customer_id)
            flash("Kayıt başarılı. Email onayı gönderildi.", "success")
            return redirect(url_for("user.login"))
        except Exception as e:
            logger.error(f"Kayıt hatası: {e}")
            flash("Kayıt sırasında hata oluştu.", "danger")
            return render_template("register.html")
    return render_template("register.html")

@user_bp.route("/activate/<token>")
def activate(token):
    email = confirm_token(token)
    if not email:
        flash("Email doğrulama başarısız.", "danger")
        return redirect(url_for("user.login"))
    mongo.db.customers.update_one({"Email": email}, {"$set": {"confirmed": True}})
    flash("Email doğrulandı. Giriş yapabilirsiniz.", "success")
    return redirect(url_for("user.login"))

@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        user = mongo.db.customers.find_one({"Email": email})
        if user and check_password_hash(user["Password"], password):
            if user.get("2fa_enabled"):
                session["pending_user_id"] = user["CustomerID"]
                return redirect(url_for("user.two_factor"))
            else:
                session["customer_name"] = user["CustomerName"]
                session["customer_id"] = user["CustomerID"]
                session["customer_type"] = user["CustomerType"]
                log_event("login", f"{user['CustomerName']} giriş yaptı.", user["CustomerID"])
                if user["CustomerType"] == "Admin":
                    return redirect(url_for("order.order_panel"))
                else:
                    return redirect(url_for("user.profile"))
        else:
            flash("Geçersiz email veya şifre.", "danger")
    return render_template("login.html")

@user_bp.route("/two_factor", methods=["GET", "POST"])
def two_factor():
    if request.method == "POST":
        otp = request.form.get("otp")
        pending_user_id = session.get("pending_user_id")
        if not pending_user_id:
            flash("Geçersiz oturum.", "danger")
            return redirect(url_for("user.login"))
        user = mongo.db.customers.find_one({"CustomerID": pending_user_id})
        if user and user.get("2fa_enabled") and user.get("2fa_secret"):
            totp = pyotp.TOTP(user["2fa_secret"])
            if totp.verify(otp):
                session["customer_name"] = user["CustomerName"]
                session["customer_id"] = user["CustomerID"]
                session["customer_type"] = user["CustomerType"]
                session.pop("pending_user_id", None)
                log_event("login", f"{user['CustomerName']} giriş yaptı (2FA).", user["CustomerID"])
                if user["CustomerType"] == "Admin":
                    return redirect(url_for("order.order_panel"))
                else:
                    return redirect(url_for("user.profile"))
            else:
                flash("Geçersiz doğrulama kodu.", "danger")
        else:
            flash("2FA etkin değil.", "danger")
    return render_template("two_factor.html")


@user_bp.route("/enable_2fa", methods=["GET", "POST"])
def enable_2fa():
    if not session.get("customer_id"):
        flash("Lütfen giriş yapınız.", "danger")
        return redirect(url_for("user.login"))
    user = mongo.db.customers.find_one({"CustomerID": session["customer_id"]})
    if not user.get("2fa_secret"):
        secret = pyotp.random_base32()
        mongo.db.customers.update_one({"CustomerID": user["CustomerID"]}, {"$set": {"2fa_secret": secret}})
        user["2fa_secret"] = secret
    totp = pyotp.TOTP(user["2fa_secret"])
    otp_auth_url = totp.provisioning_uri(name=user["Email"], issuer_name="Sipariş Yönetimi")

    if request.method == "POST":
        otp = request.form.get("otp")
        if totp.verify(otp):
            mongo.db.customers.update_one({"CustomerID": user["CustomerID"]}, {"$set": {"2fa_enabled": True}})
            flash("2FA başarıyla etkinleştirildi.", "success")
            return redirect(url_for("user.profile"))
        else:
            flash("Doğrulama kodu hatalı.", "danger")
    return render_template("enable_2fa.html", otp_auth_url=otp_auth_url, secret=user["2fa_secret"])


@user_bp.route("/disable_2fa", methods=["GET", "POST"])
def disable_2fa():
    if not session.get("customer_id"):
        flash("Lütfen giriş yapınız.", "danger")
        return redirect(url_for("user.login"))
    user = mongo.db.customers.find_one({"CustomerID": session["customer_id"]})
    if not user.get("2fa_secret"):
        flash("2FA ayarları mevcut değil.", "danger")
        return redirect(url_for("user.profile"))
    totp = pyotp.TOTP(user["2fa_secret"])

    if request.method == "POST":
        otp = request.form.get("otp")
        if totp.verify(otp):
            mongo.db.customers.update_one({"CustomerID": user["CustomerID"]}, {"$set": {"2fa_enabled": False}})
            flash("2FA başarıyla devre dışı bırakıldı.", "success")
            return redirect(url_for("user.profile"))
        else:
            flash("Doğrulama kodu hatalı.", "danger")
    return render_template("disable_2fa.html", secret=user["2fa_secret"])


@user_bp.route("/profile", methods=["GET", "POST"], endpoint="profile")
def profile():
    if not session.get("customer_id"):
        flash("Giriş yapmalısınız.", "danger")
        return redirect(url_for("user.login"))
    customer = mongo.db.customers.find_one({"CustomerID": session["customer_id"]})
    if not customer:
        flash("Kullanıcı bulunamadı.", "danger")
        return redirect(url_for("user.login"))
    if request.method == "POST":
        budget_str = request.form.get("budget", "").strip()
        try:
            budget = float(budget_str)
        except ValueError:
            return jsonify({"success": False, "message": "Geçerli bütçe giriniz."}), 400
        if budget < 0:
            return jsonify({"success": False, "message": "Bütçe negatif olamaz."}), 400
        try:
            mongo.db.customers.update_one({"CustomerID": session["customer_id"]}, {"$set": {"Budget": budget}})
            log_event("budget_updated", f"Bakiye güncellendi: {budget}", session["customer_id"])
            return jsonify({"success": True, "message": "Bakiye güncellendi."}), 200
        except Exception as e:
            logger.error(f"Bakiye güncelleme hatası: {e}")
            return jsonify({"success": False, "message": "Güncelleme sırasında hata oluştu."}), 500
    return render_template("profile.html", customer=customer)

@user_bp.route("/change_password", methods=["GET", "POST"])
def change_password():
    if not session.get("customer_id"):
        flash("Lütfen giriş yapınız.", "danger")
        return redirect(url_for("user.login"))
    if request.method == "POST":
        current_password = request.form.get("current_password")
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        if new_password != confirm_password:
            return jsonify({"success": False, "message": "Yeni şifreler uyuşmuyor."}), 400
        user = mongo.db.customers.find_one({"CustomerID": session["customer_id"]})
        if not user or not check_password_hash(user["Password"], current_password):
            return jsonify({"success": False, "message": "Mevcut şifre yanlış."}), 400
        try:
            mongo.db.customers.update_one(
                {"CustomerID": session["customer_id"]},
                {"$set": {"Password": generate_password_hash(new_password)}}
            )
            log_event("password_changed", f"{user['CustomerName']} şifresini değiştirdi.", session["customer_id"])
            return jsonify({"success": True, "message": "Şifre başarıyla değiştirildi."})
        except Exception as e:
            logger.error(f"Şifre güncelleme hatası: {e}")
            return jsonify({"success": False, "message": "Güncelleme sırasında hata oluştu."}), 500
    return render_template("change_password.html")

@user_bp.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if request.method == "POST":
        email = request.form.get("email")
        user = mongo.db.customers.find_one({"Email": email})
        if user:
            token = generate_confirmation_token(email)
            reset_url = url_for("user.reset_password", token=token, _external=True)
            msg = Message("Şifre Sıfırlama", recipients=[email])
            msg.html = render_template("reset_password_email.html", reset_url=reset_url)
            mail.send(msg)
            log_event("reset_password_request", f"Şifre sıfırlama talebi: {email}", user["CustomerID"])
            return jsonify({"success": True, "message": "Şifre sıfırlama linki gönderildi.", "reset_url": reset_url})
        else:
            return jsonify({"success": False, "message": "Email bulunamadı."}), 404
    return render_template("reset_password_request.html")

@user_bp.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if request.method == "POST":
        new_password = request.form.get("new_password")
        confirm_password = request.form.get("confirm_password")
        if new_password != confirm_password:
            return jsonify({"success": False, "message": "Şifreler uyuşmuyor."}), 400
        email = confirm_token(token)
        if not email:
            return jsonify({"success": False, "message": "Token geçersiz veya süresi dolmuş."}), 400
        mongo.db.customers.update_one({"Email": email}, {"$set": {"Password": generate_password_hash(new_password)}})
        log_event("reset_password", f"{email} için şifre sıfırlandı.", email)
        return jsonify({"success": True, "message": "Şifre başarıyla sıfırlandı."}), 200
    return render_template("reset_password.html")
@user_bp.route("/logout", endpoint="logout")
def logout():
    if session.get("customer_name"):
        log_event("logout", f"{session['customer_name']} çıkış yaptı.", session.get("customer_id"))
    session.clear()
    flash("Başarıyla çıkış yaptınız.", "success")
    return redirect(url_for("user.login"))
