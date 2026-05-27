from flask import Blueprint

seller = Blueprint('seller', __name__, template_folder='templates')

from app.seller import routes
