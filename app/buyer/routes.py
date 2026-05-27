from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Order, DirectMessage
from app.utils.decorators import buyer_required


buyer = Blueprint('buyer', __name__, url_prefix='/buyer')


@buyer.route('/buyer')
@login_required
@buyer_required
def profile():
    return render_template(
        'buyer/profile.html',
        buyer=current_user.buyer_profile
    )

@buyer.route('/dashboard')
@login_required
@buyer_required
def dashboard():
    return render_template('buyer/dashboard.html')

@buyer.route('/post_order')
@login_required
def post_order():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        if title:
            new_order = Order(title=title, description=description, user_id=current_user.id)
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
    ).order_by(DirectMessage.timestamp.desc()).all()

    return render_template(
        'buyer/messages.html',
        messages=messages
    )
