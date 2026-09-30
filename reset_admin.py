import os
import mysql.connector
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from app import app

load_dotenv()

email = 'admin@maaran.com'
name = 'Maaran Cars Admin'
password = 'Admin@123'
hash_value = generate_password_hash(password)

conn = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST', '127.0.0.1'),
    port=int(os.getenv('MYSQL_PORT', '3306')),
    user=os.getenv('MYSQL_USER', 'root'),
    password=os.getenv('MYSQL_PASSWORD', ''),
    database=os.getenv('MYSQL_DATABASE', 'maaran_cars'),
)
cur = conn.cursor(dictionary=True)
cur.execute("SELECT id FROM users WHERE email = %s", (email,))
row = cur.fetchone()
if row:
    cur.execute(
        "UPDATE users SET full_name = %s, password_hash = %s, role = 'admin' WHERE email = %s",
        (name, hash_value, email),
    )
else:
    cur.execute(
        "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, 'admin')",
        (name, email, hash_value),
    )
conn.commit()
cur.execute("SELECT full_name, email, role FROM users WHERE email = %s", (email,))
print('DB_ROW=', cur.fetchone())
cur.close()
conn.close()

with app.test_client() as client:
    resp = client.post('/api/admin/login', data={'email': email, 'password': password})
    print('STATUS=', resp.status_code)
    print('BODY=', resp.get_json())
