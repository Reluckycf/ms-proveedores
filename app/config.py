import os
from dotenv import load_dotenv
from playhouse.db_url import connect

load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

# Peewee's connect uses 'mysql://' and knows to use pymysql if installed
# or we can pass the driver explicitly, but 'mysql://' is usually enough
# if we have pymysql installed.

db = connect(DB_URL)

def init_db():
    if db.is_closed():
        db.connect(reuse_if_open=True)
