from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.models import User, MessageThread, DirectMessage, db
from datetime import datetime

messaging = Blueprint('messaging', __name__)

@messaging.route('/messages')
@login_required
def inbox():
    threads = MessageThread.query.filter(
        (MessageThread.buyer_id == current_user.id) | 
        (MessageThread.seller_id == current_user.id)
    ).order_by(MessageThread.updated_at.desc()).all()

    # Contextual template rendering based on the user's active role
    template_path = 'seller/dashboard.html' if current_user.role == 'seller' else 'buyer/dashboard.html'
    return render_template(template_path, threads=threads, active_page='messages')


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
    
    for msg in thread.messages:
        messages.append({
            "id": msg.id,
            "body": msg.body,
            "sender_id": msg.sender_id,
            "is_mine": msg.sender_id == current_user.id,
            "time": msg.created_at.strftime("%I:%M %p").lower()
        })
    
    return jsonify({
        "other_user_name": other_user.username,
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