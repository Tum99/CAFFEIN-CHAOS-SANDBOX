from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.models import Product, db


products = Blueprint('products', __name__)

@products.route('/products/')
def list_products():
    all_products = Product.query.all()
    return render_template(
        'products/product_list.html', 
        products=all_products,
        body_class='page-products')



@products.route('/products/new', methods=['GET', 'POST'])
@login_required
def create_product():
    if current_user.role != 'seller':
        return "Unauthorized", 403

    if request.method == 'POST':
        name = request.form['name']
        desc = request.form['description']
        price = request.form['price']

        product = Product(
            name=name,
            description=desc,
            price=float(price),
            seller_id=current_user.id
        )
        db.session.add(product)
        db.session.commit()

        return redirect(url_for('products.list_products'))

    return render_template('products/new.html')
