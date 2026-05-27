import os
# We import the factory and db from the 'app' package
from app import create_app, db
# We import the models from the models file inside the app package
from app.models import Product, ProductImage

# 1. Initialize the app context so SQLAlchemy knows which DB to talk to
app = create_app()

def slugify(text):
    return text.lower().replace(" ", "-")

def link_images():
    with app.app_context():
        # 2. Path based on your screenshot: static/Images/Product-images
        image_folder = os.path.join(app.static_folder, 'Images', 'Product-images')
        
        if not os.path.exists(image_folder):
            print(f"❌ Error: Folder {image_folder} not found.")
            return

        products = Product.query.all()
        
        for product in products:
            found = False
            # Check for different extensions
            for ext in ['.jpg', '.png', '.jpeg', '.webp']:
                filename = slugify(product.name) + ext
                file_path = os.path.join(image_folder, filename)
                
                if os.path.exists(file_path):
                    # Check if already linked
                    existing = ProductImage.query.filter_by(
                        product_id=product.id, 
                        image_path=filename
                    ).first()
                    
                    if not existing:
                        new_img = ProductImage(image_path=filename, product_id=product.id)
                        db.session.add(new_img)
                        print(f"✅ Linked: {filename} -> {product.name}")
                    else:
                        print(f"ℹ️ Already linked: {product.name}")
                    
                    found = True
                    break # Stop looking for other extensions for this product
            
            if not found:
                print(f"❓ No image found for: {product.name} (checked {slugify(product.name)}.*)")

        db.session.commit()
        print("🚀 Seeding Finished!")

if __name__ == "__main__":
    link_images()