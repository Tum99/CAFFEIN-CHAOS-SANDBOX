from app import create_app, db
from app.models import Category, Product

app = create_app()
with app.app_context():
    print("=== DATABASE INTEGRITY REPORT ===")
    total_cats = Category.query.count()
    total_prods = Product.query.filter_by(product_type='menu').count()
    print(f"Categories found in DB: {total_cats}")
    print(f"Menu Products found in DB: {total_prods}")
    
    # Check the first category and see if products are actually tied to it
    first_cat = Category.query.order_by(Category.display_order.asc()).first()
    if first_cat:
        print(f"\nTesting Category: '{first_cat.name}' (ID: {first_cat.id})")
        # Direct relationship check
        print(f"-> Relational products count: {len(first_cat.products)}")
        
        # Manual query check
        manual_query = Product.query.filter_by(category_id=first_cat.id).all()
        print(f"-> Manual foreign key query match count: {len(manual_query)}")