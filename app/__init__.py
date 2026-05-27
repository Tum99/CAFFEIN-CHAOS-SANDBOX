from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

import os


# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()


# Redirect unauthorized users to login page
login_manager.login_view = "auth.login"
login_manager.login_message_category = "info"


def create_app():
    app = Flask(__name__)

    # This check allows you to use SQLite locally but PostgreSQL on Render
    database_url = os.environ.get("DATABASE_URL", "sqlite:///local.db")
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    secret_key = os.environ.get("SECRET_KEY")

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SECRET_KEY'] = secret_key
    app.config['UPLOAD_FOLDER'] = os.path.join('app', 'static', 'uploads')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["WTF_CSRF_ENABLED"] = True

    csrf = CSRFProtect(app)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    

    from app import models

    # Flask-Login user loader
    from app.models import User


    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from app.main.routes import main
    from app.auth.routes import auth
    from app.services.routes import services
    from app.buyer.routes import buyer
    from app.seller.routes import seller
    from app.events.routes import events
    from app.products.routes import products
    from app.menu.routes import menu
    from app.admin.routes import admin
    

    app.register_blueprint(main)
    app.register_blueprint(auth)
    app.register_blueprint(services)
    app.register_blueprint(buyer)
    app.register_blueprint(seller)
    app.register_blueprint(events)
    app.register_blueprint(products)
    app.register_blueprint(menu)
    app.register_blueprint(admin)
    

    @app.route('/test-products')
    def test_products():
        return "Products route is alive"

    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)

    with app.app_context():
        # This ensures your coffee product tables are created on launch
        db.create_all()


    return app



