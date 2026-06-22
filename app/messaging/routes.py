from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import User, MessageThread, FarmProfile, DirectMessage, db
from datetime import datetime

messaging = Blueprint('messaging', __name__)

@messaging.route('/messages')
@login_required
def inbox():
    if current_user.role == 'seller':
        farm = FarmProfile.query.filter_by(user_id=current_user.id).first()
        if not farm or not farm.is_setup_complete:
            flash("Please complete your farm profile setup first.", "info")
            return redirect(url_for('seller.seller_setup'))

        threads = MessageThread.query.filter(
            (MessageThread.buyer_id  == current_user.id) |
            (MessageThread.seller_id == current_user.id)
        ).order_by(MessageThread.updated_at.desc()).all()

        return render_template('seller/dashboard.html',
            threads=threads,
            active_page='messages',
            farm=farm,
            listings=[],
            orders=[],
            product_earnings={},
            monthly_labels=[],
            monthly_amounts=[],
            max_amount=1,
            this_month_earnings='0',
            total_gross='0',
            pending_payout='0',
            commission='0',
            net_earnings='0',
            unread_count=0,
            has_listings=False,
            has_orders=False
        )
        
    # Buyer — no setup required, load normally
    threads = MessageThread.query.filter(
        (MessageThread.buyer_id  == current_user.id) |
        (MessageThread.seller_id == current_user.id)
    ).order_by(MessageThread.updated_at.desc()).all()

    return render_template('buyer/dashboard.html',
        threads=threads,
        active_page='messages'
    )

@messaging.route('/api/messages/<int:thread_id>')
@login_required
def get_thread_messages(thread_id):
    thread = MessageThread.query.get_or_404(thread_id)
    
    # Security: Ensure current user belongs to this thread
    if current_user.id not in [thread.buyer_id, thread.seller_id]:
        return jsonify({"error": "Unauthorized"}), 403
        
    messages = []
    # Check who the "other user" is relative to current_user
    other_user = thread.seller if current_user.id == thread.buyer_id else thread.buyer
    other_name = other_user.first_name or other_user.email.split('@')[0]
    
    for msg in thread.messages:
        messages.append({
            "id": msg.id,
            "body": msg.body,
            "sender_id": msg.sender_id,
            "is_mine": msg.sender_id == current_user.id,
            "time": msg.created_at.strftime("%I:%M %p").lower()
        })
    
    return jsonify({
        "other_user_name": other_user.email,
        "messages": messages
    })


@messaging.route('/api/messages/<int:thread_id>/send', methods=['POST'])
@login_required
def send_message(thread_id):
    thread = MessageThread.query.get_or_404(thread_id)
    
    # Security: Ensure current user belongs to this thread
    if current_user.id not in [thread.buyer_id, thread.seller_id]:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    if not data or not data.get('body'):
        return jsonify({"error": "Empty message"}), 400

    # Dynamically compute receiver_id using your current database layout properties
    receiver_id = thread.seller_id if current_user.id == thread.buyer_id else thread.buyer_id

    new_msg = DirectMessage(
        thread_id=thread.id,
        sender_id=current_user.id,
        receiver_id=receiver_id, # Safely satisfying model structural integrity constraint
        body=data.get('body')
    )
    
    # Touch thread timestamp to pull it to top of inbox listings view panel
    thread.updated_at = datetime.utcnow()
    
    db.session.add(new_msg)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": {
            "body": new_msg.body,
            "time": new_msg.created_at.strftime("%I:%M %p").lower()
        }
    })


# ── START NEW THREAD ──────────────────────────────────────────
# Called from marketplace "Message Grower" button
@messaging.route('/api/messages/start', methods=['POST'])
@login_required
def start_thread():
    data      = request.get_json()
    seller_id = data.get('seller_id')
    body      = data.get('body', '').strip()

    if not seller_id or not body:
        return jsonify({"error": "seller_id and body are required"}), 400

    seller_user = User.query.get(seller_id)
    if not seller_user:
        return jsonify({"error": "Seller not found"}), 404

    # Prevent buyers from messaging themselves
    if current_user.id == seller_id:
        return jsonify({"error": "Cannot message yourself"}), 400

    # Check if a thread already exists between these two users
    existing_thread = MessageThread.query.filter(
        (
            (MessageThread.buyer_id  == current_user.id) &
            (MessageThread.seller_id == seller_id)
        ) | (
            (MessageThread.buyer_id  == seller_id) &
            (MessageThread.seller_id == current_user.id)
        )
    ).first()

    if existing_thread:
        # Reuse existing thread
        thread = existing_thread
    else:
        # Create a new thread
        thread = MessageThread(
            buyer_id=current_user.id,
            seller_id=seller_id
        )
        db.session.add(thread)
        db.session.flush()

    # Add the opening message
    new_msg = DirectMessage(
        thread_id=thread.id,
        sender_id=current_user.id,
        receiver_id=seller_id,
        body=body
    )
    thread.updated_at = datetime.utcnow()
    db.session.add(new_msg)
    db.session.commit()

    return jsonify({
        "status":    "success",
        "thread_id": thread.id,
        "message":   "Thread started"
    })


# ── UNREAD COUNT (AJAX — for navbar badge) ────────────────────
@messaging.route('/api/messages/unread-count')
@login_required
def unread_count():
    count = DirectMessage.query.filter_by(
        receiver_id=current_user.id,
        is_read=False
    ).count()
    return jsonify({"unread": count})
# PYEOF
# echo "messaging routes done"