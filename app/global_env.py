import os
CONFIG = None
TABLE = None
from dotenv import load_dotenv

def load_config():
    load_dotenv()
    global CONFIG
    global TABLE
    CONFIG = {
        "AWS_ACCESS_KEY_ID": os.getenv("AWS_ACCESS_KEY_ID"),
        "AWS_SECRET_ACCESS_KEY": os.getenv("AWS_SECRET_ACCESS_KEY"),
        "BUCKET_NAME": os.getenv("BUCKET_NAME"),
        "CONNECTION_STR": os.getenv("CONNECTION_STR"),
        "MAIN_DB": os.getenv("MAIN_DB")
    }
    TABLE = {
        "CUSTOMER_TABLE": os.getenv("CUSTOMER_TABLE"),
        "COURIER_TABLE": os.getenv("COURIER_TABLE"),
        "ORDER_TABLE": os.getenv("ORDER_TABLE"),
        "DICTIONARY_TABLE": os.getenv("DICTIONARY_TABLE")
    }

def get_config():
    return CONFIG , TABLE