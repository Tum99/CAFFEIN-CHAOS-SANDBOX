from flask import Blueprint

messaging = Blueprint('messaging', __name__)

from app.messaging import routes
