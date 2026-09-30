# The Maaran Cars

A responsive vehicle showcase and registration website for The Maaran Cars, built with plain HTML, CSS, JavaScript, Flask, and MySQL. Buyers and sellers use separate forms; submissions are saved permanently with an automatic registration ID and timestamp.

## Project structure

- `app.py` - Flask routes, validation, password hashing, and MySQL connection
- `templates/index.html` - public company page and registration choices
- `templates/buyer_register.html` - buyer registration form
- `templates/seller_register.html` - seller vehicle registration form
- `templates/admin_dashboard.html` - protected buyer and seller records dashboard
- `static/css/style.css` - responsive visual system
- `static/js/app.js` - form submission and modal interactions
- `schema.sql` - MySQL database, users, buyer registrations, and seller registrations
- `.env.example` - local configuration template

## Run locally

1. Create a MySQL database by running `schema.sql` in MySQL Workbench or the MySQL client.
2. Copy `.env.example` to `.env` and fill in your MySQL password and a strong `SECRET_KEY`.
3. Create and activate a virtual environment:

   ```powershell
   C:/Users/ELCOT/AppData/Local/Python/pythoncore-3.14-64/python.exe -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

4. Install packages:

   ```powershell
   python -m pip install -r requirements.txt
   ```

5. Start the development server:

   ```powershell
   flask --app app run --debug
   ```

Open `http://127.0.0.1:5000` in a browser.

## Admin account and dashboard

Generate a password hash with Werkzeug, then add an admin row using the commented example in `schema.sql`:

```powershell
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('replace-me'))"
```

After logging in from the Admin login button, the app redirects to `/admin/dashboard`. The dashboard requires the Flask session created at login and displays all saved buyer and seller records. Use `/admin/logout` to end the session.
