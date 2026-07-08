from flask import Blueprint, render_template, request, redirect, url_for, jsonify, flash
from flask_login import login_required, current_user
from app.models import User, MessageThread, FarmProfile, DirectMessage, FarmProductListing, GrowerBuyerTransaction, Product, db
from datetime import datetime
from collections import defaultdict

messaging = Blueprint('messaging', __name__)


# ── INBOX ─────────────────────────────────────────────────────
@messaging.route('/messages')
@login_required
def inbox():
    if current_user.role == 'seller':
        farm = FarmProfile.query.filter_by(user_id=current_user.id).first()
        if not farm or not farm.is_setup_complete:
            flash("Please complete your farm profile setup first.", "info")
            return redirect(url_for('seller.seller_setup'))

    # Same query for both buyer and seller
    threads = MessageThread.query.filter(
        (MessageThread.buyer_id  == current_user.id) |
        (MessageThread.seller_id == current_user.id)
    ).order_by(MessageThread.updated_at.desc()).all()

    return render_template('messaging/messages.html', threads=threads)


# ── GET THREAD MESSAGES (AJAX) ────────────────────────────────
@messaging.route('/api/messages/<int:thread_id>')
@login_required
def get_thread_messages(thread_id):
    thread = MessageThread.query.get_or_404(thread_id)

    if current_user.id not in [thread.buyer_id, thread.seller_id]:
        return jsonify({"error": "Unauthorized"}), 403

    # Mark messages as read for current user
    DirectMessage.query.filter_by(
        thread_id=thread_id,
        receiver_id=current_user.id,
        is_read=False
    ).update({"is_read": True})
    db.session.commit()

    other_user = thread.seller if current_user.id == thread.buyer_id else thread.buyer
    other_name = other_user.first_name or other_user.email.split('@')[0]

    messages = []
    for msg in thread.messages:
        messages.append({
            "id":        msg.id,
            "body":      msg.body,
            "sender_id": msg.sender_id,
            "is_mine":   msg.sender_id == current_user.id,
            "time":      msg.created_at.strftime("%I:%M %p").lower()
        })

    return jsonify({
        "thread_id":       thread.id,
        "other_user_name": other_name,
        "other_user_id":   other_user.id,
        "messages":        messages
    })


# ── SEND MESSAGE (AJAX) ───────────────────────────────────────
@messaging.route('/api/messages/<int:thread_id>/send', methods=['POST'])
@login_required
def send_message(thread_id):
    thread = MessageThread.query.get_or_404(thread_id)

    if current_user.id not in [thread.buyer_id, thread.seller_id]:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()
    if not data or not data.get('body', '').strip():
        return jsonify({"error": "Empty message"}), 400

    receiver_id = thread.seller_id if current_user.id == thread.buyer_id else thread.buyer_id

    new_msg = DirectMessage(
        thread_id=thread.id,
        sender_id=current_user.id,
        receiver_id=receiver_id,
        body=data['body'].strip()
    )
    thread.updated_at = datetime.utcnow()
    db.session.add(new_msg)
    db.session.commit()

    return jsonify({
        "status": "success",
        "message": {
            "id":      new_msg.id,
            "body":    new_msg.body,
            "is_mine": True,
            "time":    new_msg.created_at.strftime("%I:%M %p").lower()
        }
    })


# ── START NEW THREAD ──────────────────────────────────────────
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

    if current_user.id == seller_id:
        return jsonify({"error": "Cannot message yourself"}), 400

    # Find or create thread
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
        thread = existing_thread
    else:
        thread = MessageThread(
            buyer_id=current_user.id,
            seller_id=seller_id
        )
        db.session.add(thread)
        db.session.flush()

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


# ── UNREAD COUNT ──────────────────────────────────────────────
@messaging.route('/api/messages/unread-count')
@login_required
def unread_count():
    count = DirectMessage.query.filter_by(
        receiver_id=current_user.id,
        is_read=False
    ).count()
    return jsonify({"unread": count})