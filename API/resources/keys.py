import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()  # Adds .env to memory
# postgres db connection
postgres_options = {
    "host": os.getenv("POSTGRES_HOST"),
    "database": os.getenv("POSTGRES_DATABASE"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD")
    }


db_conn = psycopg2.connect(**postgres_options)
c = db_conn.cursor()


private_keys: list = ((os.getenv("PRIVATE_KEYS")).split(','))

idol_folder = os.getenv("FOLDER_LOCATION")

top_gg_webhook_key = os.getenv("TOP_GG_WEBHOOK")
