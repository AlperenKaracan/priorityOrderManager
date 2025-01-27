from flask import Flask, render_template, session
from extensions import mongo
from models import init_db
from resources.customer import customer_bp
from resources.order import order_bp
from resources.product import product_bp
from resources.log import log_bp
from resources.auth import auth_bp
from user import user_bp
from utils.worker import start_worker_threads

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/order_management"
app.secret_key = "supersecretkey"

mongo.init_app(app)

with app.app_context():
    if mongo.db.customers.count_documents({}) == 0:
        init_db()

app.register_blueprint(customer_bp, url_prefix="/customers")
app.register_blueprint(order_bp, url_prefix="/order")
app.register_blueprint(product_bp, url_prefix="/product")
app.register_blueprint(log_bp, url_prefix="/logs")
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(user_bp, url_prefix="/user")

@app.template_filter('datetimeformat')
def datetimeformat(timestamp):
    try:
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        return "Geçersiz Zaman Damgası"
start_worker_threads()

@app.route("/")
def index():
    logged_in_user = session.get("customer_name", None)
    return render_template("index.html", logged_in_user=logged_in_user)

if __name__ == "__main__":
    app.run(debug=False)


