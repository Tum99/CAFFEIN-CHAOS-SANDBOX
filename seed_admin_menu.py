# seed_admin_menu.py
from app import create_app, db
from app.models import (
    User, Category, Product,
    FarmProfile, FarmProductListing, Service
)
from werkzeug.security import generate_password_hash
from datetime import date

app = create_app()
app.app_context().push()


# ══════════════════════════════════════════════════════
# 1. ADMIN USER
# ══════════════════════════════════════════════════════
admin_email    = "faithadmin@testing.com"
admin_password = "password123"

admin_user = User.query.filter_by(role='admin').first()
if not admin_user:
    admin_user = User(
        email=admin_email,
        phone=700000000,
        password=generate_password_hash(admin_password, method="pbkdf2:sha256"),
        role="admin"
    )
    db.session.add(admin_user)
    db.session.commit()
    print(f"✅ Admin created: {admin_email}")
else:
    print("ℹ️  Admin already exists")


# ══════════════════════════════════════════════════════
# 2. GROWER USER
# ══════════════════════════════════════════════════════
# grower_email    = "julyia.grower@testing.com"
# grower_password = "password123"

# grower_user = User.query.filter_by(email=grower_email).first()
# if not grower_user:
#     grower_user = User(
#         email=grower_email,
#         phone=722000001,
#         password=generate_password_hash(grower_password, method="pbkdf2:sha256"),
#         role="seller"
#     )
#     db.session.add(grower_user)
#     db.session.commit()
#     print(f"✅ Grower user created: {grower_email}")
# else:
#     print("ℹ️  Grower user already exists")


# ══════════════════════════════════════════════════════
# 3. MENU CATEGORIES
# ══════════════════════════════════════════════════════
category_names = [
    "Fan Favourites",
    "Black Coffee",
    "Granito",
    "Flavoured Coffee",
    "Cold Coffee",
    "Speciality of Espresso",
    "Manual Brew",
    "Fruity Magnet",
    "Caffein Shake",
    "Sinful Cho Shake",
    "Hot Coffee",
    "Beverages",
    "Desserts"
]

for index, name in enumerate(category_names):
    category = Category.query.filter_by(name=name).first()
    if not category:
        category = Category(name=name, display_order=index)
        db.session.add(category)
    else:
        category.display_order = index

db.session.commit()
print("✅ Categories added")


# ══════════════════════════════════════════════════════
# 4. MENU PRODUCTS  (product_type="menu", is_available=True)
# ══════════════════════════════════════════════════════
products_data = {
    "Black Coffee": [
        {"name": "Dopio",        "price": 250, "description": "Strong double espresso"},
        {"name": "Irish Coffee", "price": 350, "description": "Coffee with a touch of whiskey"},
        {"name": "Romana",       "price": 200, "description": "Italian classic espresso"},
        {"name": "Americano",    "price": 200, "description": "Espresso topped with hot water"},
        {"name": "Affogato",     "price": 300, "description": "Espresso poured over ice cream"},
        {"name": "Red Eye",      "price": 300, "description": "Drip coffee with a shot of espresso"}
    ],
    "Granito": [
        {"name": "Mango Crush",             "price": 700, "description": "Refreshing mango granita"},
        {"name": "Blue Curacao",            "price": 700, "description": "Blue citrus icy drink"},
        {"name": "Kiwi Crush",             "price": 700, "description": "Kiwi flavored icy delight"},
        {"name": "Strawberry Kiwi Tango",   "price": 700, "description": "Strawberry and kiwi granita blend"},
        {"name": "Orange Crush",            "price": 700, "description": "Citrus orange granita"},
        {"name": "Strawberry Orange Tango", "price": 700, "description": "Fruity strawberry orange blend"}
    ],
    "Flavoured Coffee": [
        {"name": "Nutty Milano",           "price": 600, "description": "Hazelnut espresso blend"},
        {"name": "Caramel Classic",        "price": 600, "description": "Caramel coffee delight"},
        {"name": "Espresso Madness",       "price": 600, "description": "Double shot espresso with chocolate"},
        {"name": "Frozen Coffee Rum",      "price": 600, "description": "Frozen coffee with a rum twist"},
        {"name": "Cinamon Freeze",         "price": 600, "description": "Cinnamon spiced frozen coffee"},
        {"name": "Coffee Chocolate Shake", "price": 600, "description": "Coffee blended with rich chocolate"}
    ],
    "Cold Coffee": [
        {"name": "Iced Mocha",      "price": 500, "description": "Chocolate iced coffee"},
        {"name": "Caffein Frappe",  "price": 600, "description": "Blended coffee frappe"},
        {"name": "Caffein Freeze",  "price": 500, "description": "Frozen coffee drink"},
        {"name": "Iced Latte",      "price": 500, "description": "Espresso with cold milk over ice"},
        {"name": "Iced Cappuchino", "price": 500, "description": "Chilled cappuccino over ice"},
        {"name": "Caffein Culture", "price": 500, "description": "Our signature cold coffee blend"}
    ],
    "Manual Brew": [
        {"name": "Chemex Coffee", "price": 600, "description": "Clean, bright pour-over in a Chemex"},
        {"name": "Hario V60",     "price": 600, "description": "Precise V60 pour-over method"},
        {"name": "Mocha Pot",     "price": 600, "description": "Stovetop Moka pot espresso"},
        {"name": "French Press",  "price": 600, "description": "Full immersion French Press brew"},
        {"name": "Siphon",        "price": 800, "description": "Theatrical siphon vacuum brewing"},
        {"name": "Aero Press",    "price": 600, "description": "Smooth, versatile AeroPress brew"}
    ],
    "Speciality of Espresso": [
        {"name": "Ristretto",  "price": 250, "description": "Short, concentrated espresso shot"},
        {"name": "Espresso",   "price": 250, "description": "Classic single shot espresso"},
        {"name": "Lungo",      "price": 250, "description": "Long, mild espresso pull"},
        {"name": "Flat White", "price": 300, "description": "Velvety microfoam over double ristretto"},
        {"name": "Cortado",    "price": 300, "description": "Equal parts espresso and warm milk"}
    ],
    "Fruity Magnet": [
        {"name": "Apple Pitch",      "price": 600, "description": "Fresh apple flavoured drink"},
        {"name": "Strawberry Punch", "price": 600, "description": "Vibrant strawberry punch"},
        {"name": "Mango & Kiwi",     "price": 600, "description": "Tropical mango and kiwi blend"},
        {"name": "Orange Dawa",      "price": 600, "description": "Citrus orange dawa style drink"}
    ],
    "Beverages": [
        {"name": "Hot Lemon Ginger", "price": 300, "description": "Soothing lemon and ginger tea"},
        {"name": "Pineapple Dawa",   "price": 300, "description": "Pineapple dawa style cooler"},
        {"name": "Hibiscus Dawa",    "price": 300, "description": "Floral hibiscus infused dawa"},
        {"name": "Roibos Tea",       "price": 300, "description": "South African rooibos herbal tea"}
    ],
    "Sinful Cho Shake": [
        {"name": "Choco Chip Shake",   "price": 750,  "description": "Creamy shake with chocolate chips"},
        {"name": "Kit Kat Shake",      "price": 800,  "description": "Kit Kat blended milkshake"},
        {"name": "Oreo Shake",         "price": 750,  "description": "Classic Oreo cookie shake"},
        {"name": "Bouborn Shake",      "price": 800,  "description": "Bourbon biscuit blended shake"},
        {"name": "M & M Shake",        "price": 800,  "description": "M&M chocolate candy shake"},
        {"name": "Ferro Rocher Shake", "price": 1000, "description": "Luxury Ferrero Rocher milkshake"}
    ],
    "Caffein Shake": [
        {"name": "Caramel Shake",     "price": 600, "description": "Rich caramel coffee milkshake"},
        {"name": "Hezelnut Shake",    "price": 600, "description": "Hazelnut flavoured coffee shake"},
        {"name": "Peppermint Shake",  "price": 600, "description": "Cool peppermint coffee shake"},
        {"name": "Fudge Milkshake",   "price": 600, "description": "Thick fudge chocolate milkshake"},
        {"name": "Vanilla Milkshake", "price": 600, "description": "Classic vanilla bean milkshake"},
        {"name": "Caffein Milkshake", "price": 600, "description": "Our signature coffee milkshake"}
    ],
    "Hot Coffee": [
        {"name": "Macchiato",     "price": 400, "description": "Espresso with a dash of foamed milk"},
        {"name": "Coffee Lite",   "price": 450, "description": "Light roast, smooth and easy"},
        {"name": "Hot Chocolate", "price": 400, "description": "Rich creamy hot chocolate"},
        {"name": "Cafe Latte",    "price": 450, "description": "Espresso with steamed milk"},
        {"name": "Cappuchino",    "price": 350, "description": "Equal espresso, milk and foam"},
        {"name": "Cafe Mocha",    "price": 450, "description": "Espresso, chocolate and steamed milk"}
    ],
    "Desserts": [
        {"name": "Caffein Addiction",  "price": 500,  "description": "Espresso-soaked dessert delight"},
        {"name": "Caffein Madness",    "price": 500,  "description": "Layered coffee dessert"},
        {"name": "Caffein Temptation", "price": 500,  "description": "Decadent coffee and cream dessert"},
        {"name": "Choco Brownie",      "price": 1000, "description": "Rich fudgy chocolate brownie"},
        {"name": "Mochalito",          "price": 500,  "description": "Mocha-inspired dessert cup"},
        {"name": "Caramelo",           "price": 500,  "description": "Caramel custard dessert"}
    ]
}

for cat_name, items in products_data.items():
    category = Category.query.filter_by(name=cat_name).first()
    if category:
        for p in items:
            existing = Product.query.filter_by(
                name=p["name"],
                category_id=category.id
            ).first()
            if not existing:
                product = Product(
                    seller_id=admin_user.id,
                    name=p["name"],
                    price=p["price"],
                    stock=1,
                    description=p["description"],
                    category_id=category.id,
                    product_type="menu",
                    is_available=True
                )
                db.session.add(product)

db.session.commit()
print("✅ Menu products added")


# ══════════════════════════════════════════════════════
# 5. APPAREL PRODUCTS
# ══════════════════════════════════════════════════════
apparel_products = [
    {
        "name": "Take a Step Tee — Brown",
        "price": 2500,
        "description": "100% cotton oversized tee. 'Take a Step' footprint print on back. C&C logo on chest.",
        "stock": 50
    },
    {
        "name": "Take a Step Tee — Olive Green",
        "price": 2500,
        "description": "Same signature design in forest green. Cream footprint print.",
        "stock": 50
    },
    {
        "name": "Take a Step Varsity Jacket",
        "price": 7500,
        "description": "Brown body, cream sleeves. CHAOS on left arm, CAFFEINE on right. Limited run.",
        "stock": 20
    },
    {
        "name": "Caffeine & Chaos Apron",
        "price": 3200,
        "description": "Canvas cross-back apron with leather accents. C&C logo on chest pocket.",
        "stock": 30
    },
    {
        "name": "Timba-XO Collab Apron",
        "price": 3500,
        "description": "Limited edition Timba-XO x Caffeine & Chaos collaboration apron.",
        "stock": 15
    }
]

for p in apparel_products:
    existing = Product.query.filter_by(
        name=p["name"],
        product_type="apparel"
    ).first()
    if not existing:
        product = Product(
            seller_id=admin_user.id,
            name=p["name"],
            price=p["price"],
            stock=p["stock"],
            description=p["description"],
            category_id=None,
            product_type="apparel",
            is_available=True
        )
        db.session.add(product)

db.session.commit()
print("✅ Apparel products added")


# ══════════════════════════════════════════════════════
# 6. MERCH PRODUCTS
# FIX: Original had "if not existing" OUTSIDE the for loop
#      so only the last item in the list was ever checked.
#      Now correctly indented inside the loop.
# ══════════════════════════════════════════════════════
merch_products = [
    {
        "name": "C&C Signature Tumbler",
        "price": 1800,
        "description": "Double-walled stainless tumbler. Keeps drinks cold 24hrs, hot 12hrs.",
        "stock": 40
    },
    {
        "name": "Branded Wood Slice Stand",
        "price": 950,
        "description": "Hand-cut natural wood slice with C&C logo burned in. Set of 2.",
        "stock": 25
    },
    {
        "name": "C&C Branded Cup — Green",
        "price": 600,
        "description": "Takeaway cup with the Caffeine & Chaos logo. Pack of 10.",
        "stock": 100
    },
    {
        "name": "C&C Enamel Mug",
        "price": 1200,
        "description": "Vintage-style enamel mug with C&C logo. Perfect for outdoor brewing.",
        "stock": 35
    }
]

for p in merch_products:
    existing = Product.query.filter_by(
        name=p["name"],
        product_type="merch"
    ).first()
    if not existing:            # FIX: now inside the for loop
        product = Product(
            seller_id=admin_user.id,
            name=p["name"],
            price=p["price"],
            stock=p["stock"],
            description=p["description"],
            category_id=None,
            product_type="merch",
            is_available=True
        )
        db.session.add(product)

db.session.commit()
print("✅ Merch products added")


# ══════════════════════════════════════════════════════
# 7. FARM PROFILE
# FIX: profile_image → farm_image (matches model field name)
# ══════════════════════════════════════════════════════
farm = FarmProfile.query.filter_by(user_id=grower_user.id).first()
if not farm:
    farm = FarmProfile(
        user_id=grower_user.id,
        farm_name="Jepng'etich Farm",
        location="Ziwa, Uasingishu County",
        county="Uasingishu",
        farm_size_acres=12.5,
        altitude_masl=1850,
        certifications="Organic",
        bio=(
            "Family-run coffee farm in the highlands of Uasingishu County. "
            "We grow Batian and SL28 varieties at 1,850m above sea level. "
            "Our coffee is known for its premium citrus profile with a molasses finish."
        ),
        farm_image="images/farm/jepngetich-farm.jpg",  # FIX: was profile_image
        is_verified=True,
        is_live=True,
        is_setup_complete=True
    )
    db.session.add(farm)
    db.session.commit()
    print("✅ Farm profile created")
else:
    print("ℹ️  Farm profile already exists")


# ══════════════════════════════════════════════════════
# 8. FARM PRODUCTS + LISTINGS
# FIX: Original was cut off mid-loop — completed here
# FIX: FarmProductListing now includes grower_id (required column)
# ══════════════════════════════════════════════════════
# farm_products_data = [
#     {
#         "product": {
#             "name": "Arabica Batian — 250g",
#             "price": 850,
#             "description": "Medium roast. Batian varietal. Notes of citrus with a molasses finish.",
#             "stock": 200
#         },
#         "listing": {
#             "varietal": "Batian",
#             "process": "Washed",
#             "roast_level": "Medium",
#             "harvest_date": date(2025, 10, 15),
#             "quantity_kg": 50.0,
#             "minimum_order_kg": 0.25,
#             "price_per_kg": 3400,
#             "tasting_notes": "Citrus, Molasses, Dark Berry",
#             "status": "available"
#         }
#     }
# ]

# for entry in farm_products_data:
#     p = entry["product"]
#     l = entry["listing"]

#     existing = Product.query.filter_by(
#         name=p["name"],
#         product_type="farm"
#     ).first()

#     if not existing:
#         product = Product(
#             seller_id=grower_user.id,
#             name=p["name"],
#             price=p["price"],
#             stock=p["stock"],
#             description=p["description"],
#             category_id=None,
#             product_type="farm",
#             is_available=True
#         )
#         db.session.add(product)
#         db.session.flush()  # get product.id before the listing needs it

#         listing = FarmProductListing(
#             product_id=product.id,
#             farm_id=farm.id,
#             grower_id=grower_user.id,   # FIX: required field that was missing
#             varietal=l["varietal"],
#             process=l["process"],
#             roast_level=l["roast_level"],
#             harvest_date=l["harvest_date"],
#             quantity_kg=l["quantity_kg"],
#             minimum_order_kg=l["minimum_order_kg"],
#             price_per_kg=l["price_per_kg"],
#             tasting_notes=l["tasting_notes"],
#             status=l["status"]
#         )
#         db.session.add(listing)

# db.session.commit()
# print("✅ Farm products and listings added")


# ══════════════════════════════════════════════════════
# 9. SERVICES
# FIX: Completely missing from original file
# ══════════════════════════════════════════════════════
services_data = [
    {
        "name": "Coffee Catering",
        "description": (
            "We set up a full specialty coffee bar at your event. From espresso to cold brew, "
            "our baristas bring the full C&C experience to your venue. "
            "Weddings, corporate events, pop-ups."
        ),
        "price": 15000,
        "category": "catering"
    },
    {
        "name": "Barista Training",
        "description": (
            "Learn the craft from our team. From beginner home brewing to professional "
            "barista techniques. One-on-one or group sessions available."
        ),
        "price": 3500,
        "category": "training"
    },
    {
        "name": "Farm Listing",
        "description": (
            "Are you a coffee grower? List your farm and products on the C&C platform. "
            "Connect directly with buyers, set your prices, and manage your sales."
        ),
        "price": 0,
        "category": "platform"
    },
    {
        "name": "Coffee Subscription",
        "description": (
            "Get freshly roasted Kenyan coffee delivered to your door every month. "
            "Choose your roast, grind, and quantity. Cancel anytime."
        ),
        "price": 1200,
        "category": "subscription"
    },
    {
        "name": "Event Hosting",
        "description": (
            "Host your next get-together at the C&C space. Coffee, community, and a vibe "
            "that is hard to find elsewhere. Available for private bookings."
        ),
        "price": 8000,
        "category": "events"
    },
    {
        "name": "Brand Collaboration",
        "description": (
            "We are open to creative partnerships. Co-branded products, joint events, "
            "pop-up collaborations. Let us build something together."
        ),
        "price": 0,
        "category": "partnership"
    }
]

for s in services_data:
    existing = Service.query.filter_by(name=s["name"]).first()
    if not existing:
        service = Service(
            name=s["name"],
            description=s["description"],
            price=s["price"],
            category=s["category"],
            seller_id=admin_user.id
        )
        db.session.add(service)

db.session.commit()
print("✅ Services added")


# ══════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════
print("")
print("🎉 Seeding complete!")
print("─────────────────────────────────────────")
print(f"  Admin user    : {admin_email}")
print(f"  Grower user   : {grower_email}")
print(f"  Categories    : {len(category_names)}")
print(f"  Menu items    : {sum(len(v) for v in products_data.values())}")
print(f"  Apparel items : {len(apparel_products)}")
print(f"  Merch items   : {len(merch_products)}")
print(f"  Farm products : {len(farm_products_data)}")
print(f"  Services      : {len(services_data)}")
print("─────────────────────────────────────────")