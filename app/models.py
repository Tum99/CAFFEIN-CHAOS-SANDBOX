from datetime import datetime
from flask_login import UserMixin
from app import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.Integer, unique=True, nullable=False)
    # buyer / seller / admin
    role = db.Column(db.String(20), nullable=False)
    profile_pic = db.Column(db.String(255), default='default_user.jpg')

    # Relationships
    products = db.relationship(
        "Product",
        backref="seller",
        lazy=True
    )

    services = db.relationship(
        "Service",
        backref="seller",
        lazy=True
    )

    messages_sent = db.relationship(
        "DirectMessage",
        foreign_keys="DirectMessage.sender_id",
        backref="sender",
        lazy=True
    )

    messages_received = db.relationship(
        "DirectMessage",
        foreign_keys="DirectMessage.receiver_id",
        backref="receiver",
        lazy=True
    )

    seller_profile = db.relationship(
        "SellerProfile",
        backref="user",
        uselist=False,
        cascade="all, delete"
    )

    buyer_profile = db.relationship(
        "BuyerProfile",
        backref="user",
        uselist=False,
        cascade="all, delete"
    )

    cart_items = db.relationship(
        "CartItem",
        backref="user",
        lazy=True,
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<User {self.email}>"


class SellerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))

    bids = db.relationship("Bid", backref="seller", lazy=True)

    def __repr__(self):
        return f"<SellerProfile {self.user_id}>"


class BuyerProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    preferences = db.Column(db.Text)

    orders = db.relationship(
        "Order",
        backref="buyer",
        lazy=True,
        cascade="all, delete"
    )

    bookings = db.relationship(
        "ServiceBooking",
        backref="buyer",
        lazy=True,
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<BuyerProfile {self.user_id}>"



class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    display_order = db.Column(db.Integer, default=0)

    products = db.relationship(
        "Product",
        backref="category",
        lazy=True
    )


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    seller_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=1)
    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=True
    )

     # NEW — distinguishes what kind of product this is
    product_type = db.Column(
        db.String(30),
        nullable=False,
        default="menu"
        # options:
        # "menu"    → items on the cafe menu (coffee drinks, desserts etc.)
        # "merch"   → branded merchandise (tumbler, wood stand etc.)
        # "apparel" → clothing (tees, jackets, aprons)
        # "farm"    → raw coffee from growers (beans, lots, batches)
    )

    # NEW — only relevant for farm products
    is_available = db.Column(db.Boolean, default=True)

    images = db.relationship(
        "ProductImage",
        backref="product",
        lazy=True,
        cascade="all, delete-orphan"
    )

    cart_items = db.relationship(
        "CartItem",
        backref="product",
        lazy=True,
        cascade="all, delete"
    )

    def __repr__(self):
        return f"<Product {self.name}>"



class ProductImage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False
    )
    image_path = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<ProductImage {self.id} for Product {self.product_id}>"


class FarmProfile(db.Model):
    """
    Extra details for users who are coffee growers.
    One grower (User) has one FarmProfile.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False,
        unique=True
    )
    farm_name = db.Column(db.String(150), nullable=False)
    farm_image = db.Column(db.String(255))
    location = db.Column(db.String(150))
    county = db.Column(db.String(100))
    farm_size_acres = db.Column(db.Float)
    altitude_masl = db.Column(db.Integer)         # metres above sea level
    certifications = db.Column(db.String(255))    # e.g. "Organic, Fair Trade"
    bio = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    phone = db.Column(db.Integer)
    whatsapp_phone = db.Column(db.Integer)
    # User is done typing
    is_setup_complete = db.Column(db.Boolean, default=False)
    # If you also want to track if they are "Live" on the marketplace:
    is_live = db.Column(db.Boolean, default=False)

    # farm's coffee listings (filtered from Product table)
    @property
    def farm_products(self):
        return Product.query.filter_by(
            seller_id=self.user_id,
            product_type="farm"
        ).all()

    def __repr__(self):
        return f"<FarmProfile {self.farm_name}>"


class FarmProductListing(db.Model):
    """
    When a grower lists a specific coffee lot/batch for sale.
    Links to the Product table but adds farm-specific trading details.
    """
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False
    )
    farm_id = db.Column(
        db.Integer,
        db.ForeignKey("farm_profile.id"),
        nullable=False
    )

    # coffee-specific details
    varietal = db.Column(db.String(100))          # e.g. Batian, SL28, Ruiru 11
    process = db.Column(db.String(50))            # Washed, Natural, Honey
    roast_level = db.Column(db.String(30))        # Light, Medium, Dark
    harvest_date = db.Column(db.Date)
    quantity_kg = db.Column(db.Float)             # total kg available
    minimum_order_kg = db.Column(db.Float, default=1.0)
    price_per_kg = db.Column(db.Float, nullable=False)
    tasting_notes = db.Column(db.String(255))     # e.g. "Citrus, Molasses, Berry"
    status = db.Column(
        db.String(20),
        default="available"
        # "available", "reserved", "sold"
    )
    listed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationships
    product = db.relationship("Product", backref="farm_listing", uselist=False)
    farm = db.relationship("FarmProfile", backref="listings")

    def __repr__(self):
        return f"<FarmProductListing {self.id} — {self.varietal}>"


class GrowerBuyerTransaction(db.Model):
    """
    Records a completed or in-progress deal between a grower and a buyer.
    Separate from the cafe's regular Order model.
    """
    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(
        db.Integer,
        db.ForeignKey("farm_product_listing.id"),
        nullable=False
    )
    buyer_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )
    grower_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )
    quantity_kg = db.Column(db.Float, nullable=False)
    agreed_price_per_kg = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(
        db.String(20),
        default="pending"
        # "pending", "confirmed", "paid", "shipped", "completed", "cancelled"
    )
    mpesa_reference = db.Column(db.String(100))   # M-Pesa transaction code
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships
    listing = db.relationship("FarmProductListing", backref="transactions")
    buyer = db.relationship(
        "User",
        foreign_keys=[buyer_id],
        backref="purchases"
    )
    grower = db.relationship(
        "User",
        foreign_keys=[grower_id],
        backref="sales"
    )

    def __repr__(self):
        return f"<Transaction {self.id} — {self.status}>"



class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    quantity = db.Column(db.Integer, default=1)


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    category = db.Column(db.String(50))  # drink / repair
    seller_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    bookings = db.relationship(
        "ServiceBooking",
        backref="service",
        lazy=True,
        cascade="all, delete"
    )


class ServiceBooking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"))
    buyer_id = db.Column(db.Integer, db.ForeignKey("buyer_profile.id"))
    status = db.Column(db.String(20), default="pending")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class DirectMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    target_type = db.Column(db.String(20))  # product / service
    target_id = db.Column(db.Integer)
    rating = db.Column(db.Integer)
    comment = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime)
    location = db.Column(db.String(255))


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    buyer_id = db.Column(
        db.Integer,
        db.ForeignKey("buyer_profile.id", ondelete="CASCADE")
    )
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bids = db.relationship(
        "Bid",
        backref="order",
        lazy=True,
        cascade="all, delete"
    )


class Bid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"))
    seller_id = db.Column(db.Integer, db.ForeignKey("seller_profile.id"))
    offer_price = db.Column(db.Float)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    ingredients = db.Column(db.Text)
    steps = db.Column(db.Text)
    category = db.Column(db.String(50))  # latte / espresso / cold brew