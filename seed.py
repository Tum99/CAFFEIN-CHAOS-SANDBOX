import os

# FIX 1: Load .env BEFORE create_app() so DATABASE_URL is available
from dotenv import load_dotenv
load_dotenv()

# We import the factory and db from the 'app' package
from app import create_app, db
# We import the models from the models file inside the app package
from app.models import Product, ProductImage

# Initialize the app context so SQLAlchemy knows which DB to talk to
app = create_app()


def slugify(text):
    return text.lower().replace(" ", "-")


def link_images():
    with app.app_context():

        # FIX 2: Try both capitalizations of the folder name
        # so it works regardless of how the folder was created
        possible_folders = [
            os.path.join(app.static_folder, 'images', 'Product-images'),  # lowercase
            os.path.join(app.static_folder, 'Images', 'Product-images'),  # uppercase
        ]

        image_folder = None
        for folder in possible_folders:
            if os.path.exists(folder):
                image_folder = folder
                print(f"📁 Found image folder: {folder}")
                break

        if not image_folder:
            print("❌ Error: Could not find Product-images folder.")
            print("   Checked:")
            for f in possible_folders:
                print(f"     {f}")
            print("   Make sure your images are in one of those paths.")
            return

        # FIX 3: Build a case-insensitive lookup of actual files on disk
        # so "Romana.jpg" matches the slug "romana.jpg"
        actual_files = {}
        for f in os.listdir(image_folder):
            actual_files[f.lower()] = f  # key=lowercase, value=real filename

        print(f"🖼️  {len(actual_files)} image files found on disk")
        print(f"🛍️  Checking {Product.query.count()} products...\n")

        linked   = 0
        skipped  = 0
        missing  = 0

        products = Product.query.all()

        for product in products:
            found = False

            for ext in ['.jpg', '.png', '.jpeg', '.webp']:
                # Build the slug filename and look it up case-insensitively
                slug_filename = slugify(product.name) + ext
                real_filename = actual_files.get(slug_filename.lower())

                if real_filename:
                    file_path = os.path.join(image_folder, real_filename)

                    # Check if already linked to avoid duplicates
                    existing = ProductImage.query.filter_by(
                        product_id=product.id,
                        image_path=real_filename
                    ).first()

                    if not existing:
                        new_img = ProductImage(
                            image_path=real_filename,
                            product_id=product.id
                        )
                        db.session.add(new_img)
                        print(f"  ✅ Linked : {real_filename} → {product.name}")
                        linked += 1
                    else:
                        print(f"  ℹ️  Already: {product.name}")
                        skipped += 1

                    found = True
                    break

            if not found:
                print(f"  ❓ Missing : {product.name}  (looked for: {slugify(product.name)}.*)")
                missing += 1

        db.session.commit()

        print(f"\n{'─' * 45}")
        print(f"  ✅ Newly linked : {linked}")
        print(f"  ℹ️  Already done : {skipped}")
        print(f"  ❓ No image     : {missing}")
        print(f"{'─' * 45}")
        print("🚀 Image linking complete!")

        # FIX 4: Print all files in the folder so you can see
        # what names exist and compare to what slugify produces
        if missing > 0:
            print(f"\n📂 Files in {os.path.basename(image_folder)}:")
            for f in sorted(actual_files.values()):
                print(f"   {f}")


if __name__ == "__main__":
    link_images()