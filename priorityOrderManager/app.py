from flask import Flask, render_template, session
from extensions import mongo, mail
from models import init_db
from resources.customer import customer_bp
from resources.order import order_bp
from resources.product import product_bp
from resources.log import log_bp
from resources.auth import auth_bp
from resources.user import user_bp
from utils.worker import start_worker_threads
from datetime import datetime
from resources.admin import admin_bp
app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/db_name"
app.secret_key = " "

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "MAIL_USERNAME"
app.config["MAIL_PASSWORD"] = "MAIL_PASSWORD"
app.config["MAIL_DEFAULT_SENDER"] = "MAIL_DEFAULT_SENDER"

mongo.init_app(app)
mail.init_app(app)

with app.app_context():
    if mongo.db.customers.count_documents({}) == 0:
        init_db()

app.register_blueprint(customer_bp, url_prefix="/customers")
app.register_blueprint(order_bp, url_prefix="/order")
app.register_blueprint(product_bp, url_prefix="/product")
app.register_blueprint(log_bp, url_prefix="/logs")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(admin_bp)

@app.template_filter('datetimeformat')
def datetimeformat(timestamp):
    try:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return "Invalid Timestamp"

start_worker_threads()

@app.route("/")
def index():
    logged_in_user = session.get("customer_name")
    return render_template("index.html", logged_in_user=logged_in_user)

if __name__ == "__main__":
    app.run(debug=True)
