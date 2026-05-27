from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, TextAreaField, SelectField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email, Length
from app.models import Category

class AdminRegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Register Admin')


class CategoryForm(FlaskForm):
    name = StringField("Category Name", validators=[DataRequired()])
    submit = SubmitField("Add Category")


class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired()])
    price = DecimalField("Price", validators=[DataRequired()])
    description = TextAreaField("Description")

    category = SelectField("Category", coerce=int)

    submit = SubmitField("Add Product")

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        self.category.choices = [
            (c.id, c.name) for c in Category.query.all()
        ]