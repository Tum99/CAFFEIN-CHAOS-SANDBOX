from flask import Blueprint

events = Blueprint('events', __name__, template_folder='templates')

from app.events import routes
