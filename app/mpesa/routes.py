# app/mpesa/routes.py
# ─────────────────────────────────────────────────────────────
# M-Pesa payment routes:
#
# POST /mpesa/initiate          ← called by marketplace JS "Pay via M-Pesa"
# POST /mpesa/callback          ← called by Safaricom after payment
# GET  /mpesa/status/<tx_id>    ← called by JS to poll payment status
# POST /mpesa/message-grower    ← called by "Message Grower First" button
# ─────────────────────────────────────────────────────────────
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from app.models import (
    db, FarmProductListing, GrowerBuyerTransaction,
    MessageThread, DirectMessage, User
)
from app.mpesa.utils import stk_push
from app.utils.decorators import buyer_required
from datetime import datetime

mpesa = Blueprint('mpesa', __name__, url_prefix='/mpesa')


# ── INITIATE STK PUSH ─────────────────────────────────────────
# Called by marketplace.js handleOrder()
@mpesa.route('/initiate', methods=['POST'])
@login_required
@buyer_required
def initiate_payment():
    data = request.get_json()

    listing_id = data.get('listing_id')
    quantity   = float(data.get('quantity', 0))
    phone      = data.get('phone') or str(current_user.phone)

    # Validate inputs
    if not listing_id or quantity <= 0:
        return jsonify({'success': False, 'error': 'Invalid listing or quantity'}), 400

    listing = FarmProductListing.query.get(listing_id)
    if not listing:
        return jsonify({'success': False, 'error': 'Listing not found'}), 404

    if listing.status != 'available':
        return jsonify({'success': False, 'error': 'This listing is no longer available'}), 400

    if quantity < listing.minimum_order_kg:
        return jsonify({
            'success': False,
            'error': f'Minimum order is {listing.minimum_order_kg} kg'
        }), 400

    if quantity > listing.quantity_kg:
        return jsonify({
            'success': False,
            'error': f'Only {listing.quantity_kg} kg available'
        }), 400

    total_amount = round(quantity * listing.price_per_kg, 2)

    # Create a pending transaction record first
    # so we can match it when the callback arrives
    transaction = GrowerBuyerTransaction(
        listing_id=listing.id,
        buyer_id=current_user.id,
        grower_id=listing.grower_id,
        quantity_kg=quantity,
        agreed_price_per_kg=listing.price_per_kg,
        total_amount=total_amount,
        status='pending'
    )
    db.session.add(transaction)
    db.session.commit()

    # Initiate STK push
    result = stk_push(
        phone=phone,
        amount=total_amount,
        account_ref=f'CC{transaction.id}',   # CC = Caffeine & Chaos
        description='Coffee Order'
    )

    if result['success']:
        # Store the checkout request ID so callback can find this transaction
        transaction.mpesa_reference = result['checkout_request_id']
        db.session.commit()

        return jsonify({
            'success':             True,
            'transaction_id':      transaction.id,
            'checkout_request_id': result['checkout_request_id'],
            'message':             'STK push sent. Enter your M-Pesa PIN on your phone.'
        })
    else:
        # STK push failed — delete the pending transaction
        db.session.delete(transaction)
        db.session.commit()

        return jsonify({
            'success': False,
            'error':   result.get('error', 'Payment initiation failed')
        }), 500


# ── SAFARICOM CALLBACK ────────────────────────────────────────
# Safaricom calls this URL after the buyer enters their PIN
# Must be publicly accessible — this is why we needed Render
@mpesa.route('/callback', methods=['POST'])
def mpesa_callback():
    data = request.get_json(silent=True) or {}
    current_app.logger.info(f"M-Pesa callback received: {data}")

    try:
        body            = data.get('Body', {})
        stk_callback    = body.get('stkCallback', {})
        result_code     = stk_callback.get('ResultCode')
        checkout_req_id = stk_callback.get('CheckoutRequestID')

        # Find the transaction by checkout request ID
        transaction = GrowerBuyerTransaction.query.filter_by(
            mpesa_reference=checkout_req_id
        ).first()

        if not transaction:
            current_app.logger.warning(f"No transaction found for CheckoutRequestID: {checkout_req_id}")
            return jsonify({'ResultCode': 0, 'ResultDesc': 'Accepted'}), 200

        if result_code == 0:
            # Payment successful
            # Extract M-Pesa receipt number from callback metadata
            callback_metadata = stk_callback.get('CallbackMetadata', {})
            items = callback_metadata.get('Item', [])

            mpesa_receipt = None
            for item in items:
                if item.get('Name') == 'MpesaReceiptNumber':
                    mpesa_receipt = item.get('Value')
                    break

            transaction.status          = 'paid'
            transaction.mpesa_reference = mpesa_receipt or checkout_req_id
            transaction.updated_at      = datetime.utcnow()

            # Reduce available quantity on the listing
            listing = transaction.listing
            if listing:
                listing.quantity_kg = max(0, (listing.quantity_kg or 0) - transaction.quantity_kg)
                if listing.quantity_kg <= 0:
                    listing.status = 'sold'

            db.session.commit()
            current_app.logger.info(f"Transaction {transaction.id} marked as PAID. Receipt: {mpesa_receipt}")

        else:
            # Payment failed or cancelled by user
            result_desc = stk_callback.get('ResultDesc', 'Payment failed')
            transaction.status = 'cancelled'
            db.session.commit()
            current_app.logger.info(f"Transaction {transaction.id} CANCELLED. Reason: {result_desc}")

    except Exception as e:
        current_app.logger.error(f"M-Pesa callback error: {e}")

    # Always return 200 to Safaricom so they stop retrying
    return jsonify({'ResultCode': 0, 'ResultDesc': 'Accepted'}), 200


# ── PAYMENT STATUS POLL ───────────────────────────────────────
# JS polls this after STK push to check if payment completed
@mpesa.route('/status/<int:transaction_id>', methods=['GET'])
@login_required
def payment_status(transaction_id):
    transaction = GrowerBuyerTransaction.query.get_or_404(transaction_id)

    # Security — only the buyer or grower can check
    if current_user.id not in [transaction.buyer_id, transaction.grower_id]:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify({
        'transaction_id': transaction.id,
        'status':         transaction.status,
        'total_amount':   transaction.total_amount,
        'quantity_kg':    transaction.quantity_kg,
        'paid':           transaction.status == 'paid'
    })


# ── MESSAGE GROWER ────────────────────────────────────────────
# Called by marketplace "Message Grower First" button
@mpesa.route('/message-grower', methods=['POST'])
@login_required
@buyer_required
def message_grower():
    data      = request.get_json()
    seller_id = data.get('seller_id')
    body      = data.get('body', '').strip()
    listing_id = data.get('listing_id')

    if not seller_id or not body:
        return jsonify({'success': False, 'error': 'Missing seller_id or message body'}), 400

    seller = User.query.get(seller_id)
    if not seller:
        return jsonify({'success': False, 'error': 'Grower not found'}), 404

    if current_user.id == seller_id:
        return jsonify({'success': False, 'error': 'Cannot message yourself'}), 400

    # Find or create thread
    thread = MessageThread.query.filter(
        (
            (MessageThread.buyer_id  == current_user.id) &
            (MessageThread.seller_id == seller_id)
        ) | (
            (MessageThread.buyer_id  == seller_id) &
            (MessageThread.seller_id == current_user.id)
        )
    ).first()

    if not thread:
        thread = MessageThread(
            buyer_id=current_user.id,
            seller_id=seller_id
        )
        db.session.add(thread)
        db.session.flush()

    # Add the message
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
        'success':   True,
        'thread_id': thread.id,
        'message':   'Message sent to grower'
    })