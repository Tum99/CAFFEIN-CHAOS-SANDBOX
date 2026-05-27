# seed_admin_menu.py
from app import create_app, db
from app.models import User, Category, Product
from werkzeug.security import generate_password_hash

app = create_app()
app.app_context().push()

# ----- Create Admin -----
admin_email = "faithadmin@testing.com"
admin_password = "password123"

admin_user = User.query.filter_by(role='admin').first()
if not admin_user:
    admin_user = User(
        email=admin_email,
        password=generate_password_hash(admin_password, method="pbkdf2:sha256"),
        role="admin"
    )
    db.session.add(admin_user)
    db.session.commit()
    print(f"Admin created: {admin_email}")
else:
    print("Admin already exists")


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
print("Categories added")

products_data = {
    "Black Coffee": [
        {"name": "Dopio", "price": 250, "description": "Strong double espresso"},
        {"name": "Irish Coffee", "price": 350, "description": "Coffee with a touch of whiskey"},
        {"name": "Romana", "price": 200, "description": "Italian classic espresso"},
        {"name": "Americano", "price": 200, "description": "Italian classic espresso"},
        {"name": "Affogato", "price": 300, "description": "Italian classic espresso"},
        {"name": "Red Eye", "price": 300, "description": "Italian classic espresso"}
    ],
    "Granito": [
        {"name": "Mango Crush", "price": 700, "description": "Refreshing mango granita"},
        {"name": "Blue Curacao", "price": 700, "description": "Blue citrus icy drink"},
        {"name": "Kiwi Crush", "price": 700, "description": "Kiwi flavored icy delight"},
        {"name": "Strawberry Kiwi Tango", "price": 700, "description": "Italian classic espresso"},
        {"name": "Orange Crush", "price": 700, "description": "Italian classic espresso"},
        {"name": "Strawberry Orange Tango", "price": 700, "description": "Italian classic espresso"}
    ],
    "Flavoured Coffee": [
        {"name": "Nutty Milano", "price": 600, "description": "Hazelnut espresso"},
        {"name": "Caramel Classic", "price": 600, "description": "Caramel coffee delight"},
        {"name": "Espresso Madness", "price": 600, "description": "Double shot espresso with chocolate"},
        {"name": "Frozen Coffee Rum", "price": 600, "description": "Italian classic espresso"},
        {"name": "Cinamon Freeze", "price": 600, "description": "Italian classic espresso"},
        {"name": "Coffee Chocolate Shake", "price": 600, "description": "Italian classic espresso"}
        
    ],
    "Cold Coffee": [
        {"name": "Iced Mocha", "price": 500, "description": "Chocolate iced coffee"},
        {"name": "Caffein Frappe", "price": 600, "description": "Blended coffee frappe"},
        {"name": "Caffein Freeze", "price": 500, "description": "Frozen coffee drink"},
        {"name": "Iced Latte", "price": 500, "description": "Italian classic espresso"},
        {"name": "Iced Cappuchino", "price": 500, "description": "Italian classic espresso"},
        {"name": "Caffein Culture", "price": 500, "description": "Italian classic espresso"}
    ],

    "Manual Brew": [
        {"name": "Chemex Coffee", "price": 600, "description": "Chocolate iced coffee"},
        {"name": "Hario V60", "price": 600, "description": "Blended coffee frappe"},
        {"name": "Mocha Pot", "price": 600, "description": "Frozen coffee drink"},
        {"name": "French Press", "price": 600, "description": "Italian classic espresso"},
        {"name": "Siphon", "price": 800, "description": "Italian classic espresso"},
        {"name": "Aero Press", "price": 600, "description": "Italian classic espresso"}
    ],

    "Speciality of Espresso": [
        {"name": "Ristretto", "price": 250, "description": "Chocolate iced coffee"},
        {"name": "Espresso", "price": 250, "description": "Blended coffee frappe"},
        {"name": "Lungo", "price": 250, "description": "Frozen coffee drink"},
        {"name": "Flat White", "price": 300, "description": "Italian classic espresso"},
        {"name": "Cortado", "price": 300, "description": "Italian classic espresso"}
    ],

    "Fruity Magnet": [
        {"name": "Apple Pitch", "price": 600, "description": "Chocolate iced coffee"},
        {"name": "Strawberry Punch", "price": 600, "description": "Blended coffee frappe"},
        {"name": "Mango & Kiwi", "price": 600, "description": "Frozen coffee drink"},
        {"name": "Orange Dawa", "price": 600, "description": "Italian classic espresso"}
    ],

    "Beverages": [
        {"name": "Hot Lemon Ginger", "price": 300, "description": "Chocolate iced coffee"},
        {"name": "Pineapple Dawa", "price": 300, "description": "Blended coffee frappe"},
        {"name": "Hibiscus Dawa", "price": 300, "description": "Frozen coffee drink"},
        {"name": "Roibos Tea", "price": 300, "description": "Italian classic espresso"}
    ],

    "Sinful Cho Shake": [
        {"name": "Choco Chip Shake", "price": 750, "description": "Chocolate iced coffee"},
        {"name": "Kit Kat Shake", "price": 800, "description": "Blended coffee frappe"},
        {"name": "Oreo Shake", "price": 750, "description": "Frozen coffee drink"},
        {"name": "Bouborn Shake", "price": 800, "description": "Italian classic espresso"},
        {"name": "M & M Shake", "price": 800, "description": "Italian classic espresso"},
        {"name": "Ferro Rocher Shake", "price": 1000, "description": "Italian classic espresso"}
    ],

    "Caffein Shake": [
        {"name": "Caramel Shake", "price": 600, "description": "Chocolate iced coffee"},
        {"name": "Hezelnut Shake", "price": 600, "description": "Blended coffee frappe"},
        {"name": "Peppermint Shake", "price": 600, "description": "Frozen coffee drink"},
        {"name": "Fudge Milkshake", "price": 600, "description": "Italian classic espresso"},
        {"name": "Vanilla Milkshake", "price": 600, "description": "Italian classic espresso"},
        {"name": "Caffein Milkshake", "price": 600, "description": "Italian classic espresso"}
    ],

    "Hot Coffee": [
        {"name": "Macchiato", "price": 400, "description": "Chocolate iced coffee"},
        {"name": "Coffee Lite", "price": 450, "description": "Blended coffee frappe"},
        {"name": "Hot Chocolate", "price": 400, "description": "Frozen coffee drink"},
        {"name": "Cafe Latte", "price": 450, "description": "Italian classic espresso"},
        {"name": "Cappuchino", "price": 350, "description": "Italian classic espresso"},
        {"name": "Cafe Mocha", "price": 450, "description": "Italian classic espresso"}
    ],

    "Desserts": [
        {"name": "Caffein Addiction", "price": 500, "description": "Chocolate iced coffee"},
        {"name": "Caffein Madness", "price": 500, "description": "Blended coffee frappe"},
        {"name": "Caffein Temptation", "price": 500, "description": "Frozen coffee drink"},
        {"name": "Choco Brownie", "price": 1000, "description": "Italian classic espresso"},
        {"name": "Mochalito", "price": 500, "description": "Italian classic espresso"},
        {"name": "Caramelo", "price": 500, "description": "Italian classic espresso"}
    ]
}

for cat_name, products in products_data.items():
    category = Category.query.filter_by(name=cat_name).first()
    if category:
        for p in products:
            existing = Product.query.filter_by(name=p["name"], category_id=category.id).first()
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
print("Products added")

# APPAREL PRODUCTS

apparel_products = [
    {
        "name": "Take a Step Tee — Brown",
        "price": 2500,
        "description": "100% cotton oversized tee. 'Take a Step' footprint print on back. C&C logo on chest. Available S–XXL.",
        "stock": 50
    },
    {
        "name": "Take a Step Tee — Olive Green",
        "price": 2500,
        "description": "Same signature design in forest green. Cream footprint print. A nod to the farm, worn in the city.",
        "stock": 50
    },
    {
        "name": "Take a Step Varsity Jacket",
        "price": 7500,
        "description": "Brown body, cream sleeves. CHAOS on left arm, CAFFEINE on right. Footprint graphic on back. Limited run.",
        "stock": 20
    },
    {
        "name": "Caffeine & Chaos Apron",
        "price": 3200,
        "description": "Canvas cross-back apron with leather accents. C&C logo on chest pocket. 'Take a Step' on front panel.",
        "stock": 30
    },
    {
        "name": "Timba-XO Collab Apron",
        "price": 3500,
        "description": "Limited edition Timba-XO x Caffeine & Chaos collaboration apron. Canvas with leather accents.",
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


 
#MERCH PRODUCTS
merch_products = [
{
    "name": "C&C Signature Tumbler",
    "price": 1800,
    "description": "Double-walled stainless tumbler. Keeps drinks cold 24hrs, hot 12hrs. Green with cream C&C branding.",
    "stock": 40
},
{
    "name": "Branded Wood Slice Stand",
    "price": 950,
    "description": "Hand-cut natural wood slice with C&C logo burned in. As seen in our product shoots. Set of 2.",
    "stock": 25
},
{
    "name": "C&C Branded Cup — Green",
    "price": 600,
    "description": "Takeaway cup with the Caffeine & Chaos logo. Green with cream branding. Pack of 10.",
    "stock": 100
},
{
    "name": "C&C Enamel Mug",
    "price": 1200,
    "description": "Vintage-style enamel mug with C&C logo. Perfect for outdoor brewing sessions.",
    "stock": 35
}
]

for p in merch_products:
    existing = Product.query.filter_by(
        name=p["name"],
        product_type="merch"
    ).first()
if not existing:
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


# FARM PROFILE  (for the demo grower)
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
        profile_image="images/farm/jepngetich-farm.jpg",
        is_verified=True
    )
    db.session.add(farm)
    db.session.commit()
    print("✅ Farm profile created")
else:
    print("ℹ️  Farm profile already exists")



#FARM PRODUCTS + LISTINGS  (product_type = "farm")
#     These are raw coffee beans sold by the grower
# ══════════════════════════════════════════════════════
farm_products_data = [
    {
        "product": {
            "name": "Arabica Batian — 250g",
            "price": 850,
            "description": "Medium roast, medium grind. Batian varietal. Notes of citrus with a molasses finish.",
            "stock": 200
        },
        "listing": {
            "varietal": "Batian",
            "process": "Washed",
            "roast_level": "Medium",
            "harvest_date": date(2025, 10, 15),
            "quantity_kg": 50.0,
            "minimum_order_kg": 0.25,
            "price_per_kg": 3400,
            "tasting_notes": "Citrus, Molasses, Dark Berry",
            "status": "available"
        }
    },
    {
        "product": {
            "name": "Arabica Batian — 1kg",
            "price": 2800,
            "description": "Full kilogram of our signature Batian varietal. Premium citrus with molasses. For the serious coffee lover.",
            "stock": 100
        },
        "listing": {
            "varietal": "Batian",
            "process": "Washed",
            "roast_level": "Medium",
            "harvest_date": date(2025, 10, 15),
            "quantity_kg": 100.0,
            "minimum_order_kg": 1.0,
            "price_per_kg": 2800,
            "tasting_notes": "Citrus, Molasses, Dark Berry",
            "status": "available"
        }
    },
    {
        "product": {
            "name": "SL28 Natural Process — 250g",
            "price": 950,
            "description": "Natural processed SL28. Fruity and wine-like with a heavy body. Uasingishu highlands.",
            "stock": 80
        },
        "listing": {
            "varietal": "SL28",
            "process": "Natural",
            "roast_level": "Light",
            "harvest_date": date(2025, 11, 5),
            "quantity_kg": 20.0,
            "minimum_order_kg": 0.25,
            "price_per_kg": 3800,
            "tasting_notes": "Blueberry, Wine, Honey, Tropical Fruit",
            "status": "available"
        }
    },
    {
        "product": {
            "name": "Ruiru 11 — 500g",
            "price": 1400,
            "description": "Disease-resistant Ruiru 11 variety. Bold, full-bodied with chocolate and nut notes.",
            "stock": 60
        },
        "listing": {
            "varietal": "Ruiru 11",
            "process": "Washed",
            "roast_level": "Dark",
            "harvest_date": date(2025, 9, 20),
            "quantity_kg": 30.0,
            "minimum_order_kg": 0.5,
            "price_per_kg": 2800,
            "tasting_notes": "Dark Chocolate, Roasted Nuts, Brown Sugar",
            "status": "available"
        }
    }
]
 
for entry in farm_products_data:
    p = entry["product"]
    l = entry["listing"]
 
    # create the Product
    existing = Product.query.filter_by(
        name=p["name"],
        product_type="farm"
    ).first()
 
    if not existing:
        product = Product(
            seller_id=grower_user.id,
            name=p["name"],
            price=p["price"],
            stock=p["stock"],
            description=p["description"],
            category_id=None,
            product_type="farm",
            is_available=True
        )
        db.session.add(product)