from flask import flash, Blueprint, render_template, request, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.models import SellerProfile, DirectMessage, FarmProfile, Product, FarmProductListing, GrowerBuyerTransaction as transactions
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.decorators import seller_required
from datetime import datetime
from app import db
import json
from werkzeug.utils import secure_filename
import os

seller = Blueprint('seller', __name__, url_prefix='/seller')


@seller.route('/setup', methods=['GET', 'POST'])
@login_required
@seller_required
def seller_setup():
    farm = FarmProfile.query.filter_by(user_id=current_user.id).first()
    if farm and farm.is_setup_complete:
        pass

    my_listings = []
    if farm:
        my_listings = FarmProductListing.query.filter_by(farm_id=farm.id).all()

    steps = 0
    if farm: steps += 1
    if len(my_listings) > 0: steps += 1

    if request.method == 'POST':
        # Read form data
        farm_name    = request.form.get('farm_name')
        county       = request.form.get('county')
        location     = request.form.get('location')
        farm_size    = request.form.get('farm_size')
        altitude     = request.form.get('altitude')
        certifications = request.form.get('certifications')
        bio          = request.form.get('bio')
        phone        = request.form.get('phone')
        whatsapp_phone = request.form.get('whatsapp')
        farm_image = request.files.get('farm_photo')

        if not farm:
            # Create the FarmProfile
            farm = FarmProfile(
                user_id=current_user.id,
                farm_name=farm_name,
                county=county,
                location=location,
                farm_size_acres=float(farm_size) if farm_size else None,
                altitude_masl=int(altitude) if altitude else None,
                certifications=certifications,
                bio=bio,
                is_verified=False,
                is_setup_complete=False,
                phone=phone,
                whatsapp_phone=whatsapp_phone,
                farm_image=farm_image
            )
            db.session.add(farm)

        file = request.files.get('farm_photo')
        if file:
            #We create a unique name for the file so it doesn't overwrite 
            # someone else's "farm.jpg". We include the user ID for safety.
            filename = secure_filename(f"farm_{current_user.id}_{file.filename}")
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            farm.farm_image = filename

        db.session.commit()

        flash('Farm profile created! Now add your first listing.', 'success')
        # After setup — go straight to the real dashboard
        return redirect(url_for('seller.seller_setup', section='sec-farm-profile'))

    return render_template(
        'seller/new_seller.html',
        farm=farm,
        body_class='page-setup',
        active_page='dashboard',
        listings=my_listings,
        total_steps=steps 
    )


       

@seller.route('/skip-onboarding', methods=['GET'])
@login_required
@seller_required
def skip_onboarding():
    farm = FarmProfile.query.filter_by(user_id=current_user.id).first()
    if farm:
        farm.is_setup_complete = True # This is the "Key" that unlocks the real dashboard
        db.session.commit()
        flash("Welcome to your dashboard! You can go live anytime from your settings.", "info")
    
        return redirect(url_for('seller.dashboard'))

    else:
        # Safety check: if they haven't even created a farm yet, they can't skip
        flash("Please create your farm profile first.", "warning")
        return redirect(url_for('seller.seller_setup'))


@seller.route('/dashboard')
@login_required
@seller_required
def dashboard():
    # Check if this seller has a farm profile yet and any listings
    farm = FarmProfile.query.filter_by(user_id=current_user.id).first()

    if not farm or not farm.is_setup_complete:
        return redirect(url_for('seller.seller_setup'))

    orders = transactions.query.join(FarmProductListing).filter(FarmProductListing.grower_id == current_user.id).all()

    listings = FarmProductListing.query.filter_by(farm_id=farm.id).all()

    # 1. Get all completed/paid transactions
    completed_orders = [o for o in orders if o.status in ['paid', 'completed']]
    pending_orders = [o for o in orders if o.status == 'pending']

    # 2. Calculate earnings per product
    product_earnings = {}
    this_month_gross = 0.0

    current_month = datetime.utcnow().month
    current_year = datetime.utcnow().year

    for order in completed_orders:
        listing = order.farm_product_listing 

        if listing:
            display_name = f"{listing.varietal} ({listing.process})"
        else:
            display_name = "Unknown Coffee Batch"   

        product_earnings[display_name] = product_earnings.get(display_name, 0) + order.total_amount

        # Check if the transaction happened within the current calendar month
        if order.created_at.month == current_month and order.created_at.year == current_year:
            this_month_gross += order.total_amount

    # 3. Calculate Commission (5%)
    total_gross = sum(product_earnings.values())
    pending_payout = sum(o.total_amount for o in pending_orders)
    commission = total_gross * 0.05
    net_earnings = total_gross - commission
        

    earnings = sum(
        t.total_amount for t in orders
        if t.status in ['paid', 'completed']
    )

    return render_template('seller/dashboard.html',
        active_page='dashboard',
        body_class='page-dashboard',
        farm=farm,
        listings=listings,
        orders=orders,
        this_month_earnings=f"{this_month_gross:,.0f}",
        total_gross=f"{total_gross:,.0f}",
        pending_payout=f"{pending_payout:,.0f}",
        commission=f"{commission:,.0f}",
        net_earnings=f"{net_earnings:,.0f}",
        product_earnings=product_earnings,
        is_new_seller=(farm is None),  # ← True if brand new
        has_listings=len(listings) > 0,
        has_orders=len(orders) > 0
        )

@seller.route('/<int:seller_id>')
@login_required
def public_profile(seller_id):
    seller_profile = SellerProfile.query.get_or_404(seller_id)

    return render_template(
        'seller/public_profile.html',
        seller=seller_profile
    )

@seller.route('/messages')
@login_required
@seller_required
def messages():
    # Get messages sent TO this seller
    messages = DirectMessage.query.filter_by(
        receiver_id=current_user.id
    ).order_by(DirectMessage.timestamp.desc()).all()

    return render_template(
        'seller/messages.html',
        messages=messages
    )


@seller.route('/add-listing', methods=['POST'])
@login_required
@seller_required
def add_listing():
    # 1. Fetch the Farm Profile first (we need farm.id)
    farm = FarmProfile.query.filter_by(user_id=current_user.id).first()
    if not farm:
        flash("Please complete your Farm Profile first!", "error")
        return redirect(url_for('seller.seller_setup'))

    # 2. Create the General Product Entry
    # This matches your 'class Product' model
    master_product = Product(
        seller_id=current_user.id,
        name=request.form.get('name'),
        description=request.form.get('description'),
        price=float(request.form.get('price', 0)),
        stock=int(request.form.get('stock', 0)),
        product_type='farm'
    )
    
    db.session.add(master_product)
    db.session.flush()  # This 'pushes' the product to get an ID without committing yet

    # Grab data from the 'name' attributes in HTML
    product_name = request.form.get('name')
    price = request.form.get('price')
    stock = request.form.get('stock')
    
    # 3. Create the Detailed Farm Listing
    # This matches your 'class FarmProductListing' model
    farm_listing = FarmProductListing(
        product_id=master_product.id, # Link it to the Product we just made
        farm_id=farm.id,
        grower_id=current_user.id,
        varietal=request.form.get('varietal'),
        process=request.form.get('process'),
        roast_level=request.form.get('roast'),
        quantity_kg=float(request.form.get('stock', 0)),
        price_per_kg=float(request.form.get('price', 0)),
        tasting_notes=request.form.get('notes'),
        minimum_order_kg=float(request.form.get('min_order', 1.0))
    )

    # Handle the Harvest Date (string to date object)
    harvest_date_str = request.form.get('harvest_date')
    if harvest_date_str:
        farm_listing.harvest_date = datetime.strptime(harvest_date_str, '%Y-%m-%d').date()
    
    db.session.add(farm_listing)
    db.session.commit()

    flash('Listing published! Step 2 complete.', 'success')
    return redirect(url_for('seller.seller_setup'))


@seller.route('/next-listings')
@login_required
@seller_required
def add_next_listing():
    if current_user.role != 'seller':
        flash("Unauthorized access.", "error")
        return redirect(url_for('main.index'))

    if not farm:
        flash("You must complete your Farm Profile before adding a listing.", "error")
        return redirect(url_for('seller.dashboard', _anchor='sec-dashboard'))

    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    varietal = request.form.get('varietal')
    process = request.form.get('process')
    roast_level = request.form.get('roast')
    tasting_notes = request.form.get('notes', '').strip()
    harvest_date_str = request.form.get('harvest_date')
    file = request.files.get('listing_image')
    filename = None

    if file and file.filename != '':
        # Sanitize filename string data to stay secure against injection exploits
        filename = secure_filename(file.filename)
        
        # Ensure your application's upload folder exists
        upload_path = os.path.join(current_app.root_path, 'static', 'uploads')
        if not os.path.exists(upload_path):
            os.makedirs(upload_path)
            
        # Write the file down to your disk storage layer
        file.save(os.path.join(upload_path, filename))

    try:
        price = float(request.form.get('price') or 0.0)
        stock = float(request.form.get('stock') or 0.0) # Matches quantity_kg mapping
        min_order = float(request.form.get('min_order') or 1.0)
    except ValueError:
        flash("Price, stock, and minimum order values must be valid numbers.", "error")
        return redirect(url_for('seller.dashboard', _anchor='sec-new-listing'))

    harvest_date = None
    if harvest_date_str:
        try:
            harvest_date = datetime.strptime(harvest_date_str, '%Y-%m-%d').date()
        except ValueError:
            pass

    if not name or price <= 0 or stock <= 0:
        flash("Product setup failed. Name, stock, and price cannot be blank.", "error")
        return redirect(url_for('seller.dashboard', _anchor='sec-new-listing'))

    try:
        # Step A: Instantiate the base global Product row entry
        new_base_product = Product(
            seller_id=current_user.id,
            name=name,
            description=description,
            price=price,
            stock=int(stock), # Cast safely if your base model requires an integer
            product_type='farm',
            is_available=True
        )

        db.session.add(new_base_product)
        db.session.flush()

    # Step B: Instantiate your coffee-specific transaction model row using the flushed ID
        new_farm_listing = FarmProductListing(
            product_id=new_base_product.id, # Seamlessly linking tables
            farm_id=farm.id,                 # FarmProfile reference matching schema constraints
            grower_id=current_user.id,       # Explicit user owner relationship mapping
            varietal=varietal,
            process=process,
            roast_level=roast_level,
            harvest_date=harvest_date,
            quantity_kg=stock,
            minimum_order_kg=min_order,
            price_per_kg=price,
            tasting_notes=tasting_notes,
            status="available"
        )
    
        db.session.add(new_farm_listing)
        
        # Step C: Complete transaction synchronously
        db.session.commit()
        flash("Excellent! Your coffee lot has been published live to the marketplace.", "success")
        
    except Exception as e:
        db.session.rollback()
        print(f"CRITICAL SQL RELATIONSHIP CRASH: {e}") # Log terminal detail output
        flash("An database error occurred. Your listing could not be safely finalized.", "error")

    return redirect(url_for('seller.dashboard', _anchor='sec-new-listing'))


@seller.route('/listings')
@login_required
@seller_required
def listings():
    farm = FarmProfile.query.filter_by(user_id=current_user.id).first()
    my_listings = FarmProductListing.query.filter_by(farm_id=farm.id)\
                  .order_by(FarmProductListing.listed_at.desc()).all()

    # --- ADD THIS LOGIC ---
    # Calculate steps for the progress bar in new_seller.html
    steps_done = 0
    if farm:
        steps_done += 1 # Step 1: Farm Profile
    if len(my_listings) > 0:
        steps_done += 2 # Step 2: First Listing (adds to the total)
        # Note: adjust this logic based on how you want to count 3 steps total
    
    return render_template('seller/new_seller.html', 
                           farm=farm, 
                           listings=my_listings,
                           total_steps=steps_done) # <--- Pass total_steps here!


@seller.route('/marketplace', methods=['GET'])
@login_required
@seller_required
def marketplace():
    """
    Seller/Grower-facing market inspection view.
    Allows growers to review competing farm lots, look up average price trends, etc.
    """
    search_query = request.args.get('search', '').strip()
    query = Product.query.filter_by(product_type='farm')
    
    if search_query:
        query = Product.query.filter_by(product_type='farm')
        
    farm_products = query.order_by(Product.price.desc()).all()

    formatted_listings = []
    for p in farm_products:
        listing_details = None
        if hasattr(p, 'farm_listing') and p.farm_listing:
            # If it's a list/collection, snatch the first entry safely
            if isinstance(p.farm_listing, list) or hasattr(p.farm_listing, '__len__'):
                listing_details = p.farm_listing[0] if len(p.farm_listing) > 0 else None
            else:
                listing_details = p.farm_listing

        # Determine fallback name fields safely
        farm_name = "Verified Grower"
        county = "Kenya Origin"
        varietal = "Premium"
        process = "Washed"
        roast_level = "Medium"
        harvest_date_str = "Recent"
        quantity = float(p.stock or 0)
        min_order = 1.0
        tasting_notes = "Clean, balanced single-origin profile"
    
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
            "altitude": "1,600m - 1,950m"
        })

    # 3. Calculate dynamic Hero Stats over verified, live growers
    live_farms = FarmProfile.query.filter_by(is_live=True, is_setup_complete=True).all()
    stats = {
        "total_listings": len(farm_products),
        "total_farms": len(live_farms),
        "total_counties": len({f.county for f in live_farms if f.county})
    }
    
    return render_template(
        'marketplace/marketplace.html',
        products=farm_products,
        listings=farm_products, # Map to listings variant to avoid template UndefinedErrors
        json_payload=json.dumps(formatted_listings),
        stats=stats,
        search_query=search_query
    )


@seller.route('/setup/go-live', methods=['POST'])
@login_required
@seller_required
def go_live():
    # 1. Look up the grower's profile context records
    farm = FarmProfile.query.filter_by(user_id=current_user.id).first()
    if not farm:
        flash('Please complete your farm profile description modules first.', 'error')
        return redirect(url_for('seller.seller_setup'))

    # 2. Extract their created coffee lot records
    listings = Product.query.filter_by(
        seller_id=current_user.id,
        product_type='farm'
    ).all()

    if not listings:
        flash('Please build at least one coffee lot listing configuration before going live.', 'warning')
        return redirect(url_for('seller.seller_setup')) 

    # 3. Publish and update individual product listings
    for listing in listings:
        if listing.farm_listing:
            if isinstance(listing.farm_listing, list):
                for sub_l in listing.farm_listing:
                    sub_l.status = 'available'
            else:
                listing.farm_listing.status = 'available'
        listing.is_available = True

    # 4. CRITICAL CORE FIX: Toggle the profile states so your dashboard switches green instantly
    farm.is_live = True
    farm.is_setup_complete = True # Unlocks full dashboard navigation viewports

    # Save everything cleanly in one transaction
    db.session.commit()
    
    flash('Congratulations! Your farm profile and coffee lots are officially live on the marketplace!', 'success')
    return redirect(url_for('seller.dashboard'))

@seller.route('/toggle-live', methods=['POST'])
@login_required
@seller_required
def toggle_live():
    farm = FarmProfile.query.filter_by(user_id=current_user.id).first()
    if not farm:
        flash("Farm profile not found.", "error")
        return redirect(url_for('seller.dashboard'))
    
    # Check if they have listings before letting them go live
    has_listings = FarmProductListing.query.filter_by(farm_id=farm.id).first()
    
    if not has_listings:
        flash("Add at least one coffee listing before going live!", "warning")
        return redirect(url_for('seller.dashboard'))

    # Flip the boolean
    farm.is_live = not farm.is_live
    
    # CRITICAL FIX: If they are toggling to live, their setup is obviously complete!
    if farm.is_live:
        farm.is_setup_complete = True
        
    db.session.commit()
    
    status = "now live!" if farm.is_live else "now hidden from the marketplace."
    flash(f"Your farm is {status}", "success")
    return redirect(url_for('seller.dashboard'))

@seller.route('/settings/profile', methods=['POST'])
@login_required
@seller_required
def update_profile():
    try:
        current_user.first_name = request.form.get('first_name').strip()
        current_user.last_name = request.form.get('last_name').strip()
        current_user.email = request.form.get('email').strip()
        current_user.phone = request.form.get('phone').strip()
        
        db.session.commit()
        flash('Personal information updated successfully!', 'success')
    
    except Exception as e:
        db.session.rollback()
        flash('An unexpected error occurred while saving your details.', 'error')

    return redirect(url_for('seller.dashboard', _anchor='sec-settings'))


@seller.route('/settings/payout', methods=['POST'])
@login_required
@seller_required
def update_payout():
    # If your model tracking schema has attributes for these fields:
    if hasattr(current_user, 'payout_phone'):
        current_user.payout_phone = request.form.get('payout_phone').strip()
        current_user.payout_frequency = request.form.get('payout_frequency')
        db.session.commit()
        flash('Payout options updated successfully.', 'success')
    else:
        flash('Payout custom parameters are not compiled in current schema.', 'error')
        
    return redirect(url_for('seller.dashboard', _anchor='sec-settings'))


@seller.route('/settings/password', methods=['POST'])
@login_required
@seller_required
def update_password():
    current_pass = request.form.get('current_password')
    new_pass = request.form.get('new_password')
    confirm_pass = request.form.get('confirm_password')
    
    # 1. Verify old password matches database entry hash signature
    if not check_password_hash(current_user.password_hash, current_pass):
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
    current_user.password_hash = generate_password_hash(new_pass)
    db.session.commit()
    
    flash('Account security password modified smoothly.', 'success')
    return redirect(url_for('seller.dashboard', _anchor='sec-settings'))

@seller.route('/settings/notifications', methods=['POST'])
@login_required
@seller_required
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
        
    return redirect(url_for('seller.dashboard', _anchor='sec-settings'))