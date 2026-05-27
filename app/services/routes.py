from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.models import Service, ServiceBooking, db

services = Blueprint('services', __name__)

@services.route('/services')
def list_services():
    all_services = Service.query.all()
    return render_template('services/list.html', services=all_services)


@services.route('/services/<int:id>')
def view_service(id):
    service = Service.query.get_or_404(id)
    return render_template('services/view.html', service=service)


@services.route('/services/new', methods=['GET', 'POST'])
@login_required
def create_service():
    if current_user.role != 'seller':
        return "Unauthorized", 403

    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['description']
        price = request.form['price']
        category = request.form['category']

        service = Service(
            name=name,
            description=desc,
            price=float(price),
            category=category,
            seller_id=current_user.id
        )
        db.session.add(service)
        db.session.commit()

        return redirect(url_for('services.list_services'))

    return render_template('services/new.html')


@services.route('/services/book/<int:id>', methods=['POST'])
@login_required
def book_service(id):
    booking = ServiceBooking(
        service_id=id,
        buyer_id=current_user.id
    )
    db.session.add(booking)
    db.session.commit()

    return redirect(url_for('services.view_service', id=id))


@services.route('/menu')
def menu():
    """
    Public services menu (coffee, repairs, maintenance, etc.)
    """
    services_list = Service.query.order_by(Service.category, Service.name).all()

    return render_template(
        'services/services_menu.html',
        services=services_list
    )
