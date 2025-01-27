from flask import Blueprint, render_template, request, redirect, url_for, session
from extensions import mongo

user_bp = Blueprint('user', __name__)

@user_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        customer_type = request.form.get("customer_type", "Standard")
        budget = float(request.form.get("budget", 5000))
        next_id = mongo.db.customers.count_documents({}) + 1
        mongo.db.customers.insert_one({
            "CustomerID": next_id,
            "CustomerName": name,
            "Budget": budget,
            "CustomerType": customer_type,
            "TotalSpent": 0
        })
        return redirect(url_for("index"))
    return render_template("register.html")


@user_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        name = request.form.get("name")
        customer = mongo.db.customers.find_one({"CustomerName": name})
        if customer:
            session["customer_name"] = name
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Kullanıcı bulunamadı.")
    return render_template("login.html")


@user_bp.route("/logout")
def logout():
    session.pop("customer_name", None)
    return redirect(url_for("index"))
