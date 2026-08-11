from datetime import datetime
from flask_login import UserMixin
from app import db


class User(db.Model, UserMixin):
    __tablename__ = "user"

    id          = db.Column(db.Integer, primary_key=True)
    email       = db.Column(db.String(150), unique=True, nullable=False)
    first_name  = db.Column(db.String(50))
    last_name   = db.Column(db.String(50))
    password    = db.Column(db.String(200), nullable=False)
    phone       = db.Column(db.String, unique=True, nullable=True)
    role        = db.Column(db.String(20), nullable=False)   # buyer / seller / admin
    profile_pic = db.Column(db.String(255), default='default_user.jpg')

    # Relationships
    products = db.relationship("Product", backref="seller", lazy=True)

    services = db.relationship("Service", backref="seller", lazy=True)

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
    __tablename__ = "seller_profile"

    id      = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    bio     = db.Column(db.Text)
    location = db.Column(db.String(100))

    bids = db.relationship("Bid", backref="seller", lazy=True)

    def __repr__(self):
        return f"<SellerProfile {self.user_id}>"


class BuyerProfile(db.Model):
    __tablename__ = "buyer_profile"

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    preferences = db.Column(db.Text)

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

    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False, unique=True)
    display_order = db.Column(db.Integer, default=0)

    products = db.relationship("Product", backref="category", lazy=True)


class Product(db.Model):
    __tablename__ = "product"

    id          = db.Column(db.Integer, primary_key=True)
    seller_id   = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    name        = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    price       = db.Column(db.Float, nullable=False)
    stock       = db.Column(db.Integer, default=1)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    # FIX: removed the extra leading space before the comment
    # Distinguishes what kind of product this is:
    #   "menu"    → cafe menu items (drinks, desserts)
    #   "merch"   → branded merchandise (tumbler, stand)
    #   "apparel" → clothing (tees, jackets, aprons)
    #   "farm"    → raw coffee from growers
    product_type = db.Column(db.String(30), nullable=False, default="menu")

    # Whether this product is visible / available to order
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
    farm_listing = db.relationship(
        "FarmProductListing",
        back_populates="product",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Product {self.name}>"


class ProductImage(db.Model):
    __tablename__ = "product_image"

    id         = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<ProductImage {self.id} for Product {self.product_id}>"


class FarmProfile(db.Model):
    __tablename__ = "farm_profile"

    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, unique=True)
    farm_name        = db.Column(db.String(150), nullable=False)
    farm_image       = db.Column(db.String(255))
    location         = db.Column(db.String(150))
    county           = db.Column(db.String(100))
    farm_size_acres  = db.Column(db.Float)
    altitude_masl    = db.Column(db.Integer)
    certifications   = db.Column(db.String(255))
    bio              = db.Column(db.Text)
    is_verified      = db.Column(db.Boolean, default=False)
    joined_at        = db.Column(db.DateTime, default=datetime.utcnow)
    phone            = db.Column(db.Integer)
    whatsapp_phone   = db.Column(db.Integer)
    is_setup_complete = db.Column(db.Boolean, default=False)
    is_live          = db.Column(db.Boolean, default=False)

    @property
    def farm_products(self):
        return Product.query.filter_by(
            seller_id=self.user_id,
            product_type="farm"
        ).all()

    def __repr__(self):
        return f"<FarmProfile {self.farm_name}>"


class FarmProductListing(db.Model):
    __tablename__ = "farm_product_listing"

    # FIX: id declared first — avoids column ordering issues in some DB backends
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(100))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    farm_id    = db.Column(db.Integer, db.ForeignKey("farm_profile.id"), nullable=False)
    grower_id  = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Coffee-specific trading details
    varietal         = db.Column(db.String(100))   # Batian, SL28, Ruiru 11
    process          = db.Column(db.String(50))    # Washed, Natural, Honey
    roast_level      = db.Column(db.String(30))    # Light, Medium, Dark
    harvest_date     = db.Column(db.Date)
    quantity_kg      = db.Column(db.Float)
    minimum_order_kg = db.Column(db.Float, default=1.0)
    price_per_kg     = db.Column(db.Float, nullable=False)
    tasting_notes    = db.Column(db.String(255))
    listing_image    = db.Column(db.String(255), nullable=True)
    listed_at        = db.Column(db.DateTime, default=datetime.utcnow)

    # FIX: status default was breaking because the comment was inside
    #      the default= call.  Moved comment outside.
    # Values: "available", "reserved", "sold"
    status = db.Column(db.String(20), default="available")

    # Relationships
    product = db.relationship("Product", back_populates="farm_listing")
    farm    = db.relationship("FarmProfile", backref="listings")

    def __repr__(self):
        return f"<FarmProductListing {self.id} — {self.varietal}>"


class GrowerBuyerTransaction(db.Model):
    __tablename__ = "grower_buyer_transaction"

    id                 = db.Column(db.Integer, primary_key=True)
    listing_id         = db.Column(db.Integer, db.ForeignKey("farm_product_listing.id"), nullable=False)
    buyer_id           = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    grower_id          = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quantity_kg        = db.Column(db.Float, nullable=False)
    agreed_price_per_kg = db.Column(db.Float, nullable=False)
    total_amount       = db.Column(db.Float, nullable=False)
    mpesa_reference    = db.Column(db.String(100))
    notes              = db.Column(db.Text)
    created_at         = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at         = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # FIX: same comment-in-default bug fixed here too
    # Values: "pending", "confirmed", "paid", "shipped", "completed", "cancelled"
    status = db.Column(db.String(20), default="pending")

    # Relationships
    listing = db.relationship("FarmProductListing", backref="transactions")
    buyer   = db.relationship("User", foreign_keys=[buyer_id],  backref="purchases")
    grower  = db.relationship("User", foreign_keys=[grower_id], backref="sales")

    def __repr__(self):
        return f"<Transaction {self.id} — {self.status}>"


class CartItem(db.Model):
    __tablename__ = "cart_item"

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("user.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"))
    quantity   = db.Column(db.Integer, default=1)


class Service(db.Model):
    __tablename__ = "service"

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price       = db.Column(db.Float)
    category    = db.Column(db.String(50))   # catering / training / platform / subscription
    seller_id   = db.Column(db.Integer, db.ForeignKey("user.id"))

    bookings = db.relationship(
        "ServiceBooking",
        backref="service",
        lazy=True,
        cascade="all, delete"
    )


class ServiceBooking(db.Model):
    __tablename__ = "service_booking"

    id         = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey("service.id"))
    buyer_id   = db.Column(db.Integer, db.ForeignKey("buyer_profile.id"))
    status     = db.Column(db.String(20), default="pending")
    timestamp  = db.Column(db.DateTime, default=datetime.utcnow)


class MessageThread(db.Model):
    __tablename__ = "message_thread"

    id         = db.Column(db.Integer, primary_key=True)
    buyer_id   = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    seller_id  = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = db.relationship(
        "DirectMessage",
        backref="thread",
        lazy=True,
        cascade="all, delete"
    )
    buyer  = db.relationship("User", foreign_keys=[buyer_id])
    seller = db.relationship("User", foreign_keys=[seller_id])


class DirectMessage(db.Model):
    __tablename__ = "direct_message"

    id          = db.Column(db.Integer, primary_key=True)
    sender_id   = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    thread_id   = db.Column(db.Integer, db.ForeignKey("message_thread.id"), nullable=False)
    body        = db.Column(db.Text, nullable=False)
    msg_type    = db.Column(db.String(20), default='text')
    is_read     = db.Column(db.Boolean, default=False)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)
    order_id    = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)

    order = db.relationship('Order')


class Review(db.Model):
    __tablename__ = "review"

    id          = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    target_type = db.Column(db.String(20))   # product / service
    target_id   = db.Column(db.Integer)
    rating      = db.Column(db.Integer)
    comment     = db.Column(db.Text)
    timestamp   = db.Column(db.DateTime, default=datetime.utcnow)


class Event(db.Model):
    __tablename__ = "event"

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    date        = db.Column(db.DateTime)
    location    = db.Column(db.String(255))


class Order(db.Model):
    __tablename__ = "order"

    id = db.Column(db.Integer, primary_key=True)
    listing_id = db.Column(db.Integer, db.ForeignKey('farm_product_listing.id'), nullable=False)
    buyer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    seller_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quantity_kg = db.Column(db.Float, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default='In Inquiry / Pending') # Pending, Confirmed, Shipped
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    listing = db.relationship('FarmProductListing', backref='order')
    buyer = db.relationship('User', foreign_keys=[buyer_id], backref='buyer_orders')
    seller = db.relationship('User', foreign_keys=[seller_id], backref='seller_orders')


class Bid(db.Model):
    __tablename__ = "bid"

    id          = db.Column(db.Integer, primary_key=True)
    order_id    = db.Column(db.Integer, db.ForeignKey("order.id"))
    seller_id   = db.Column(db.Integer, db.ForeignKey("seller_profile.id"))
    offer_price = db.Column(db.Float)
    message     = db.Column(db.Text)
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)


class Recipe(db.Model):
    __tablename__ = "recipe"

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(200))
    ingredients = db.Column(db.Text)
    steps       = db.Column(db.Text)
    category    = db.Column(db.String(50))   # latte / espresso / cold brew