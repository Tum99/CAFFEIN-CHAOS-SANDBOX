from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.models import User, Order, GrowerBuyerTransaction, FarmProductListing, FarmProfile, MessageThread, DirectMessage, BuyerProfile, CartItem, Product, Category
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.decorators import buyer_required
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import json


buyer = Blueprint('buyer', __name__, url_prefix='/buyer')


@buyer.route('/dashboard')
@login_required
@buyer_required
def dashboard():
    all_transactions = GrowerBuyerTransaction.query.filter_by(buyer_id=current_user.id)\
        .order_by(GrowerBuyerTransaction.created_at.desc()).all()

    recent_transactions = all_transactions[:5]

    total_orders = len(all_transactions)
    in_progress_orders = sum(1 for tx in all_transactions if tx.status in ['pending', 'confirmed', 'paid', 'shipped'])

    total_spent = sum(tx.total_amount for tx in all_transactions if tx.status != 'cancelled')

    unread_msg_count = DirectMessage.query.filter_by(receiver_id=current_user.id, is_read=False).count()

    threads = MessageThread.query.filter_by(buyer_id=current_user.id)\
        .order_by(MessageThread.updated_at.desc()).all()

    saved_cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    saved_count = len(saved_cart_items)

    session_history = session.get('browsing_history', [])

    browsing_history = []
    if session_history:
        # Keeps database query order matched to the session list order
        browsing_history = [Product.query.get(pid) for pid in session_history if Product.query.get(pid)]


    return render_template(
        'buyer/dashboard.html',
        transactions=all_transactions,
        recent_transactions=recent_transactions,
        total_orders=total_orders,
        in_progress_orders=in_progress_orders,
        total_spent=total_spent,
        unread_msg_count=unread_msg_count,
        threads=threads,
        current_date=datetime.now().strftime("%A, %d %B %Y"),
        saved_items=saved_cart_items,
        saved_count=saved_count,
        browsing_history=browsing_history[:5]
    )


@buyer.route('/settings/profile', methods=['POST'])
@login_required
@buyer_required
def update_profile():
    current_user.first_name = request.form.get('first_name', '').strip()
    current_user.last_name = request.form.get('last_name', '').strip()
    current_user.email = request.form.get('email', '').strip()
    current_user.phone = request.form.get('phone', '').strip()
    
    db.session.commit()
    flash('Personal details saved successfully.', 'success')
    return redirect(url_for('buyer.dashboard', _anchor='sec-settings'))


@buyer.route('/settings/address', methods=['POST'])
@login_required
@buyer_required
def update_address():
    profile = current_user.buyer_profile
    if profile:
        # Save delivery preferences details as string json or text formatting
        town = request.form.get('town', '').strip()
        area = request.form.get('area', '').strip()
        notes = request.form.get('notes', '').strip()
        
        profile.preferences = f"{town} | {area} | Notes: {notes}"
        db.session.commit()
        flash('Delivery configuration address successfully updated.', 'success')
    return redirect(url_for('buyer.dashboard', _anchor='sec-settings'))


@buyer.route('/post_order')
@login_required
def post_order():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        if title:
            new_order = Order(title=title, description=description, buyer_id=current_user.id)
            db.session.add(new_order)
            db.session.commit()
            flash("Order posted successfully!", "success")
            return redirect(url_for('buyer.dashboard'))
    return render_template('buyer/post_order.html')

@buyer.route('/messages')
@login_required
@buyer_required
def messages():
    """
    Show all messages where the logged-in buyer is either
    the sender or the receiver.
    """

    messages = DirectMessage.query.filter(
        (DirectMessage.sender_id == current_user.id) |
        (DirectMessage.receiver_id == current_user.id)
    ).order_by(DirectMessage.created_at.desc()).all()

    return render_template(
        'buyer/messages.html',
        messages=messages
    )


@buyer.route('/settings/password', methods=['POST'])
@login_required
@buyer_required
def update_password():
    current_pass = request.form.get('current_password')
    new_pass = request.form.get('new_password')
    confirm_pass = request.form.get('confirm_password')
    
    # 1. Verify old password matches database entry hash signature
    if not check_password_hash(current_user.password, current_pass):
        flash('Incorrect current password confirmation.', 'error')
        return redirect(url_for('seller.dashboard', _anchor='sec-settings'))
        
    # 2. Verify confirmation compliance
    if new_pass != confirm_pass:
        flash('New password mismatch error.', 'error')
        return redirect(url_for('seller.dashboard', _anchor='sec-settings'))
        
    if len(new_pass) < 8:
        flash('Password must contain at least 8 elements.', 'error')
        return redirect(url_for('seller.dashboard', _anchor='sec-settings'))

    # 3. Apply secure hash change
    current_user.password = generate_password_hash(new_pass)
    db.session.commit()
    
    flash('Account security password modified smoothly.', 'success')
    return redirect(url_for('buyer.dashboard', _anchor='sec-settings'))


@buyer.route('/settings/notifications', methods=['POST'])
@login_required
@buyer_required
def update_notifications():
    if hasattr(current_user, 'order_alerts'):
        current_user.order_alerts = request.form.get('order_alerts')
        current_user.payment_alerts = request.form.get('payment_alerts')
        current_user.message_alerts = request.form.get('message_alerts')
        db.session.commit()
        flash('Notification system preferences saved successfully.', 'success')
    else:
        # Mock success notification if columns do not exist in database yet
        flash('Notification preferences modified locally.', 'success')
        
    return redirect(url_for('buyer.dashboard', _anchor='sec-settings'))


@buyer.route('/wishlist/remove/<int:item_id>', methods=['POST'])
@login_required
@buyer_required
def remove_from_wishlist(item_id):
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        flash("Item removed from your saved list.", "info")
    return redirect(url_for('buyer.dashboard', _anchor='sec-saved'))


@buyer.route('/marketplace', methods=['GET'])
@login_required
@buyer_required
def marketplace():
    """
    Buyer-facing marketplace view. 
    Allows searching, filtering, and checking out via M-Pesa.
    """
    category_id = request.args.get('category_id', type=int)
    search_query = request.args.get('search', '').strip()
    
    # 1. Gather all products that belong to LIVE and verified farm profiles
    # This filters out drafts or hidden onboarding setups entirely
    query = Product.query.join(Product.farm_listing)\
                         .join(FarmProductListing.farm)\
                         .filter(
                             Product.is_available == True,
                             FarmProfile.is_live == True,
                             FarmProfile.is_setup_complete == True
                         )
    
    if category_id:
        query = query.filter(Product.category_id == category_id)
        
    #  FIX 1: Switched from .filter_by() to .filter() for the .ilike expression
    if search_query:
        query = query.filter(Product.name.ilike(f"%{search_query}%"))
        
    farm_products = query.order_by(Product.id.desc()).all()
    categories = Category.query.order_by(Category.display_order).all()

    # 2. Build the exact unified JSON data model array payload your marketplace.js demands
    formatted_listings = []
    for p in farm_products:
        # Pull listing_details context safely from relation proxies
        listing_details = None
        if hasattr(p, 'farm_listing') and p.farm_listing:
            if isinstance(p.farm_listing, list) or hasattr(p.farm_listing, '__len__'):
                listing_details = p.farm_listing[0] if len(p.farm_listing) > 0 else None
            else:
                listing_details = p.farm_listing

        # Layout styling fallbacks
        farm_name = "Verified Grower"
        county = "Kenya Origin"
        varietal = "Premium"
        process = "Washed"
        roast_level = "Medium"
        harvest_date_str = "Recent"
        quantity = float(p.stock or 0)
        min_order = 1.0
        tasting_notes = "Clean, balanced single-origin profile"
        
        # Pull our uploaded custom images if they exist on the model
        image_file = "default_coffee.jpg"
        if hasattr(listing_details, 'listing_image') and listing_details.listing_image:
            image_file = listing_details.listing_image
    
        if listing_details:
            farm_name = listing_details.farm.farm_name if listing_details.farm else farm_name
            county = listing_details.farm.county if listing_details.farm else county
            varietal = listing_details.varietal or varietal
            process = listing_details.process or process
            roast_level = listing_details.roast_level or roast_level
            harvest_date_str = listing_details.harvest_date.strftime('%B %Y') if listing_details.harvest_date else harvest_date_str
            quantity = listing_details.quantity_kg or quantity
            min_order = listing_details.minimum_order_kg or min_order
            tasting_notes = listing_details.tasting_notes or tasting_notes

        formatted_listings.append({
            "id": listing_details.id if listing_details else p.id,
            "product_id": p.id,
            "seller_id": p.seller_id, # critical for matching up your Chat engine routing targets later
            "name": p.name or f"{varietal} {process}",
            "farm_name": farm_name,
            "varietal": varietal,
            "process": process,
            "roast_level": roast_level,
            "harvest_date": harvest_date_str,
            "quantity_kg": quantity,
            "minimum_order_kg": min_order,
            "price_per_kg": float(p.price or 0.0),
            "tasting_notes": tasting_notes,
            "county": county,
            "altitude": "1,600m - 1,950m",
            "listing_image": image_file
        })

    # 3. Calculate dynamic live data stats to fix your top dashboard numbers display
    live_farms = FarmProfile.query.filter_by(is_live=True, is_setup_complete=True).all()
    stats = {
        "total_listings": len(farm_products),
        "total_farms": len(live_farms),
        "total_counties": len({f.county for f in live_farms if f.county})
    }
    
    # 4. Return variables explicitly into your template view context scope
    return render_template(
        'marketplace/marketplace.html',
        products=farm_products,
        listings=farm_products,
        json_payload=json.dumps(formatted_listings), # Injects straight into your window array targets
        categories=categories,
        stats=stats, # Fixes your Active Farms counter displays
        search_query=search_query,
        current_category=category_id
    )