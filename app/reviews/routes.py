from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.models import Message, User, db

messages = Blueprint('messages', __name__)

@messages.route('/messages')
@login_required
def inbox():
    inbox_messages = Message.query.filter_by(receiver_id=current_user.id).all()
    return render_template('messages/inbox.html', messages=inbox_messages)


@messages.route('/messages/<int:user_id>')
@login_required
def chat(user_id):
    other_user = User.query.get_or_404(user_id)

    msgs = Message.query.filter(
        (Message.sender_id == current_user.id) & (Message.receiver_id == user_id) |
        (Message.sender_id == user_id) & (Message.receiver_id == current_user.id)
    ).order_by(Message.timestamp.asc()).all()

    return render_template('messages/chat.html', messages=msgs, other=other_user)


@messages.route('/messages/send/<int:user_id>', methods=['POST'])
@login_required
def send_message(user_id):
    content = request.form['content']

    msg = Message(
        sender_id=current_user.id,
        receiver_id=user_id,
        content=content
    )

    db.session.add(msg)
    db.session.commit()

    return redirect(url_for('messages.chat', user_id=user_id))
