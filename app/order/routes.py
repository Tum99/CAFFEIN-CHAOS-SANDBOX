from flask import Blueprint, request, jsonify, flash
from flask_login import login_required, current_user
from app.models import Order, GrowerBuyerTransaction, FarmProductListing, MessageThread, DirectMessage
from app import db

order = Blueprint('order', __name__, url_prefix='/order')

@order.route('/place-direct-order', methods=['POST'])
@login_required
def place_direct_order():
    try:
        data = request.get_json() or {}

        listing_id = data.get('listing_id')
        seller_id = data.get('seller_id')
        quantity_kg = float(data.get('quantity_kg', 0))
        total_price = float(data.get('total_price', 0))
        buyer_id = current_user.id

        if not listing_id or not seller_id or quantity_kg <= 0:
            return jsonify({'success': False, 'message': 'Invalid order details provided.'}), 400

        listing = FarmProductListing.query.get_or_404(listing_id)

        price_per_kg = total_price / quantity_kg if quantity_kg > 0 else 0.0

        # 1. Create the new Order record
        new_order = Order(
            listing_id=listing.id,
            buyer_id=buyer_id,
            seller_id=seller_id,
            quantity_kg=quantity_kg,
            total_price=total_price,
            status='In Inquiry / Pending'
        )
        db.session.add(new_order)
        db.session.flush()  # Populates new_order.id

        # 2. Create the GrowerBuyerTransaction record so seller queries find it
        new_transaction = GrowerBuyerTransaction(
            listing_id=listing.id,
            buyer_id=buyer_id,
            grower_id=listing.grower_id,
            quantity_kg=quantity_kg,
            agreed_price_per_kg=price_per_kg,
            total_amount=total_price,
            status='pending'
        )
        db.session.add(new_transaction)

        # 3. Message Thread Logic
        thread = MessageThread.query.filter(
            ((MessageThread.buyer_id == buyer_id) & (MessageThread.seller_id == seller_id)) |
            ((MessageThread.buyer_id == seller_id) & (MessageThread.seller_id == buyer_id))
        ).first()

        if not thread:
            thread = MessageThread(buyer_id=buyer_id, seller_id=seller_id)
            db.session.add(thread)
            db.session.flush()

        msg_body = f"Interested in ordering {quantity_kg}kg of {listing.varietal or 'Coffee'}."
        message = DirectMessage(
            sender_id=buyer_id,
            receiver_id=seller_id,
            thread_id=thread.id,
            order_id=new_order.id,
            body=msg_body,
            msg_type='order_card'
        )
        db.session.add(message)

        # Save all records atomically
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Order placed and message sent to grower successfully!',
            'order_id': new_order.id
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500