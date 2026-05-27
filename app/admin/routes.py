from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.admin import admin
from app.admin.forms import CategoryForm, ProductForm
from app.models import Category, Product

admin = Blueprint('admin', __name__)

@admin.route('/admin')
@login_required
def dashboard():
    if current_user.role != "admin":
        return "Unauthorized", 403

    categories = Category.query.all()
    products = Product.query.all()

    return render_template(
        "admin/dashboard.html",
        categories=categories,
        products=products
    )


#Add category
@admin.route('/add-category', methods=['GET', 'POST'])
@login_required
def add_category():
    if current_user.role != "admin":
        return "Unauthorized", 403

    form = CategoryForm()

    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        return redirect(url_for('admin.dashboard'))

    return render_template("admin/add_category.html", form=form)


#Add product
@admin.route('/add-product', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.role != "admin":
        return "Unauthorized", 403

    form = ProductForm()

    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            price=form.price.data,
            description=form.description.data,
            category_id=form.category.data
        )

        db.session.add(product)
        db.session.commit()

        return redirect(url_for('admin.dashboard'))

    return render_template("admin/add_product.html", form=form)