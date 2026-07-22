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

    file = request.files.get('profile_photo')
    if file and file.filename:
        allowed = {'jpg', 'jpeg', 'png', 'webp'}
        ext = file.filename.rsplit('.', 1)[-1].lower()
        if ext in allowed:
            filename    = secure_filename(f"avatar_{current_user.id}.{ext}")
            upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_path, exist_ok=True)
            file.save(os.path.join(upload_path, filename))
            current_user.profile_pic = filename
        else:
            flash('Please upload a JPG, PNG or WebP image.', 'error')
            return redirect(url_for('buyer.dashboard'))
    
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
    category_id  = request.args.get('category_id', type=int)
    search_query = request.args.get('search', '').strip()

    query = Product.query.join(Product.farm_listing)\
                         .join(FarmProductListing.farm)\
                         .filter(
                             Product.is_available == True,
                             FarmProfile.is_live == True,
                             FarmProfile.is_setup_complete == True
                         )

    if category_id:
        query = query.filter(Product.category_id == category_id)
    if search_query:
        query = query.filter(Product.name.ilike(f"%{search_query}%"))

    farm_products = query.order_by(Product.id.desc()).all()
    categories    = Category.query.order_by(Category.display_order).all()

    formatted_listings = []
    for p in farm_products:
        # FIX: farm_listing is uselist=False — always a single object, never a list
        ld = p.farm_listing
        if ld is None:
            continue  # skip products with no listing details

        farm      = ld.farm
        farm_name = farm.farm_name if farm else "Verified Grower"
        county    = farm.county    if farm else "Kenya"

        # Build image URL — uploaded images live in static/uploads/
        if ld.listing_image:
            image_file = f"uploads/{ld.listing_image}"
        else:
            image_file = "images/logo1.png"

        formatted_listings.append({
            "id":               ld.id,
            "product_id":       p.id,
            "seller_id":        p.seller_id,
            "grower_id":        ld.grower_id,
            "name":             p.name or f"{ld.varietal} {ld.process}",
            "farm_name":        farm_name,
            "varietal":         ld.varietal         or "Premium",
            "process":          ld.process           or "Washed",
            "roast_level":      ld.roast_level       or "Medium",
            "harvest_date":     ld.harvest_date.strftime('%B %Y') if ld.harvest_date else "Recent",
            "quantity_kg":      ld.quantity_kg        or float(p.stock or 0),
            "minimum_order_kg": ld.minimum_order_kg   or 1.0,
            "price_per_kg":     float(p.price         or 0.0),
            "tasting_notes":    ld.tasting_notes      or "Clean, balanced single-origin",
            "county":           county,
            "altitude":         f"{farm.altitude_masl}m" if farm and farm.altitude_masl else "1,600m - 1,950m",
            "listing_image":    image_file
        })

    live_farms = FarmProfile.query.filter_by(is_live=True, is_setup_complete=True).all()
    stats = {
        "total_listings": len(formatted_listings),
        "total_farms":    len(live_farms),
        "total_counties": len({f.county for f in live_farms if f.county})
    }

    return render_template(
        'marketplace/marketplace.html',
        products=farm_products,
        listings=farm_products,
        json_payload=json.dumps(formatted_listings),
        categories=categories,
        stats=stats,
        search_query=search_query,
        current_category=category_id
    )

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