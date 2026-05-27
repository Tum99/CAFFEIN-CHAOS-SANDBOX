from flask import Blueprint

buyer = Blueprint('buyer', __name__, template_folder='templates')

from app.buyer import routes
