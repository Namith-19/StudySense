import mysql.connector
import os, bcrypt
from dotenv import load_dotenv
load_dotenv()

MYSQL_HOST = os.getenv('MYSQL_HOST', 'mysql')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_DB = os.getenv('MYSQL_DB', 'studysense')

def get_conn():
    return mysql.connector.connect(
        host=MYSQL_HOST, user=MYSQL_USER, password=MYSQL_PASSWORD, database=MYSQL_DB
    )

def register_user(username, email, password):
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, email, password_hash) VALUES (%s,%s,%s)", (username, email, pw_hash))
    conn.commit()
    cur.close(); conn.close()

def validate_user(email, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, password_hash, username FROM users WHERE email=%s", (email,))
    row = cur.fetchone()
    cur.close(); conn.close()
    if not row:
        return None
    user_id, pw_hash, username = row
    if bcrypt.checkpw(password.encode(), pw_hash.encode()):
        return {'id': user_id, 'username': username}
    return None