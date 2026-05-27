from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.auth.routes import redirect_by_role
from app.models import FarmProductListing, FarmProfile

main = Blueprint('main', __name__)

@main.route('/')
def home():
    if current_user.is_authenticated:
        return redirect_by_role(current_user)

    return render_template(
        'main/index.html', 
        active_page='home', 
        body_class='page-home')

@main.route('/about')
def about():
    return render_template(
        'main/about.html',
        active_page='about', 
        body_class='page-about')

@main.route('/events')
def events():
    return render_template(
        'main/events.html', 
        active_page='events', 
        body_class='page-events')

@main.route('/marketplace')
def marketplace():
    # Only show sellers who have completed setup and toggled 'Live'
    live_listings = FarmProductListing.query.join(FarmProfile).filter(
        FarmProfile.is_live == True,
        FarmProfile.is_setup_complete == True
    ).all()
    
    return render_template('marketplace/marketplace.html', listings=live_listings)
