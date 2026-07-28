# CAFFEIN-CHAOS
Caffein and Chaos is an end-to-end full stack web application that combines a local coffee shop menu with an online store. The platform allows everyday customers to view and order from a digital cafe menu, browse a community marketplace for specialty coffee beans, and shop for official branded merchandise and apparel.

**FEATURES**

1. **Digital Cafe Menu:** An interactive menu where customers can easily browse available coffee drinks and daily cafe items.

   <img width="1920" height="1075" alt="Screenshot 2026-07-28 at 20 30 53" src="https://github.com/user-attachments/assets/f1fd7555-a65e-4a2b-8ca5-eecc94a054ea" />

   <img width="1920" height="1075" alt="Screenshot 2026-07-28 at 20 49 56" src="https://github.com/user-attachments/assets/b6c0960d-65c0-4f86-bcec-dd10570ad2b1" />


3. **Specialty Coffee Marketplace:** A dedicated online shop where local coffee growers can list and sell their roasted coffee beans directly to buyers.
   
   <img width="1920" height="1075" alt="Screenshot 2026-07-28 at 20 34 32" src="https://github.com/user-attachments/assets/fb038d74-bdc4-4e96-b2cc-0f7a110ab3e0" />


5. **Merch & Apparel Shop:** A built-in retail storefront showcasing official branded merchandise, custom clothing, and retail accessories.

   <img width="1920" height="1075" alt="Screenshot 2026-07-28 at 20 37 51" src="https://github.com/user-attachments/assets/5597cade-1c16-4b02-8eb8-1ba4de66ca05" />

   <img width="1920" height="1075" alt="Screenshot 2026-07-28 at 20 52 18" src="https://github.com/user-attachments/assets/30040661-5464-43fc-976b-07238adbfda4" />

7. **User Accounts & Dashboards:** Secure login profiles with separate views and permissions tailored specifically for general buyers, independent sellers, and shop admins.

   <img width="1920" height="1075" alt="Screenshot 2026-07-28 at 20 38 58" src="https://github.com/user-attachments/assets/1c391721-2d85-4f80-8e35-abc1b21693bc" />

---   

**Tech Stack**

- **Frontend**: HTML, CSS, Jinja2 Templates, Vanilla JavaScript  
- **Framework**: Flask (Python)  
- **Database Management**: PostgreSQL / Flask-SQLAlchemy (relational data structures modeling users, products, and inventory)  
- **Hosting**: Render

---

Follow these instructions to set up the project on your local machine for development and testing.

1. **Create a project folder and virtual environment (before cloning)**

```bash
mkdir Caffeine-Chaos
cd Caffeine-Chaos
python3 -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
```

2. **Clone the repository**
```bash
git clone https://github.com/Tum99/CAFFEIN-CHAOS-SANDBOX.git 
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**

Create a .env file in the root folder and add:
```bash
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your_secure_development_key
DATABASE_URL=postgresql://username:password@localhost:5432/caffeine_chaos_db
```

5. Initialize the Relational Schema

Run your database migrations to generate the local tables before booting up the server
```bash
flask db upgrade
```

5. **Run the application (only the app)**
```bash
flask run
```
The application will boot up locally at http://127.0.0.1:5000

---























   
