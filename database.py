import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

# Neon Postgres connection string (DATABASE_URL env se aati hai)
DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
conn.autocommit = True  # har query foran save ho

cursor = conn.cursor()

# Postgres mein AUTOINCREMENT ki jagah SERIAL hota hai
cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id SERIAL PRIMARY KEY,
    question TEXT,
    answer TEXT
)
""")
