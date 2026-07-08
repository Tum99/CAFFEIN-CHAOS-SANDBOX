from flask import Blueprint, render_template, flash, redirect, jsonify, request, url_for
from flask_login import login_required, current_user
from app.auth.routes import redirect_by_role
from app.models import FarmProductListing, FarmProfile, db
import json

main = Blueprint('main', __name__)
# Add temporarily to any routes.py
@main.route('/debug-messages')
@login_required
def debug_messages():
    from app.models import MessageThread
    threads = MessageThread.query.filter(
        (MessageThread.buyer_id  == current_user.id) |
        (MessageThread.seller_id == current_user.id)
    ).all()
    
    result = []
    for t in threads:
        result.append({
            'thread_id': t.id,
            'buyer_id':  t.buyer_id,
            'seller_id': t.seller_id,
            'current_user_id': current_user.id,
            'messages': len(t.messages)
        })
    
    return jsonify({
        'current_user_id':    current_user.id,
        'current_user_email': current_user.email,
        'threads_found':      len(threads),
        'threads':            result
    })

@main.route('/test-flash')
def test_flash():
    flash('This is a success message', 'success')
    flash('This is an error message', 'error')
    flash('This is a warning message', 'warning')
    return redirect(url_for('main.home'))

@main.route('/')
def home():
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
    # 1. Fetch only listings from growers who are fully set up and toggled 'Live'
    live_listings = FarmProductListing.query.join(FarmProfile).filter(
        FarmProfile.is_live == True,
        FarmProfile.is_setup_complete == True,
        FarmProductListing.status == 'available'  # Only show items currently in stock
    ).all()
    
    # 2. Format database rows into JSON for your marketplace.js filtering/sorting engines
    formatted_listings = []
    for item in live_listings:
        # Safe structural fallbacks to protect your templates from NoneType column crashes
        farm_name = item.farm.farm_name if item.farm else "Verified Grower"
        county = item.farm.county if item.farm else "Kenya Origin"
        
        formatted_listings.append({
            "id": item.id,
            "product_id": item.product_id,
            "name": item.name or f"{item.varietal} {item.process}",
            "farm_name": farm_name,
            "varietal": item.varietal or "Unknown",
            "process": item.process or "Washed",
            "roast_level": item.roast_level or "Medium",
            "harvest_date": item.harvest_date.strftime('%B %Y') if item.harvest_date else "Recent Harvest",
            "quantity_kg": item.quantity_kg or 0.0,
            "minimum_order_kg": item.minimum_order_kg or 1.0,
            "price_per_kg": item.price_per_kg,
            "tasting_notes": item.tasting_notes or "Clean, balanced single-origin profile",
            "county": county,
            "altitude": "1,600m - 1,950m"  # Hardcoded fallback or change to item.farm.altitude if tracked
        })

    # 3. Calculate dynamic Hero Stats over verified, live growers only
    stats = {
        "total_listings": len(live_listings),
        # Unique count of active farms with live items on display right now
        "total_farms": len({item.farm_id for item in live_listings}),
        # Unique count of active production counties on display right now
        "total_counties": len({item.farm.county for item in live_listings if item.farm and item.farm.county})
    }

    return render_template(
        'marketplace/marketplace.html', 
        listings=live_listings,
        json_payload=json.dumps(formatted_listings),
        stats=stats
    )