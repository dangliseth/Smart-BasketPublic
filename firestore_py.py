from evdev import InputDevice, categorize, ecodes

import sqlite3
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

import time
import threading

cred = credentials.Certificate(
    "smart-basket-90f82-firebase-adminsdk-jns92-b13c81b170.json"
    )
firebase_admin.initialize_app(cred)
db = firestore.client()

def init_db():
    conn = sqlite3.connect('barcode_db.sqlite')
    c = conn.cursor()
    # Create table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS products (
            barcode TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_product(barcode, name, price):
    conn = sqlite3.connect('barcode_db.sqlite')
    c = conn.cursor()
    c.execute('''
        INSERT OR REPLACE INTO products (barcode, name, price)
        VALUES (?, ?, ?)
    ''', (barcode, name, price))
    conn.commit()
    conn.close()

def view_products():
    conn = sqlite3.connect('barcode_db.sqlite')
    c = conn.cursor()
    c.execute('SELECT * FROM products')
    rows = c.fetchall()
    for row in rows:
        print(row)
    conn.close()

def get_product_info(tag):
    """
    conn = sqlite3.connect('barcode_db.sqlite')
    c = conn.cursor()
    c.execute('SELECT * FROM products WHERE barcode = ?', (barcode,))
    product = c.fetchone()
    conn.close()
    """
    items_ref = db.collection("items")
    query = items_ref.where("tags", "array_contains", tag)
    
    results = query.get()
    
    if results:
        for product in results:
            item_data = product.to_dict()
            #print(f"Retrieved product: {item_data}")  # Debug line
        return item_data  # Return a list of matched items
    else:
        print("No product found with this RFID tag")
        return None

def scan_barcode(callback=None):
    device = InputDevice('/dev/input/by-id/usb-IC_Reader_IC_Reader_08FF20171101-event-kbd')

    print("Waiting for RFID input...")

    rfid_data = ''
    for event in device.read_loop():
        if event.type == ecodes.EV_KEY:
            key_event = categorize(event)
            if key_event.keystate == key_event.key_down:  # Capture key down events only
                if key_event.keycode == 'KEY_ENTER':  # RFID data ends with Enter
                    print(f"RFID Tag: {rfid_data}")
                    product = get_product_info(rfid_data)
                    if callback:
                        callback(product, rfid_data)
                    rfid_data = ''  # Reset after reading
                else:
                    rfid_data += key_event.keycode[-1]

"""
SQLite
 Initialize database and add sample products
init_db()
add_product('8850007011149', 'powder', 10)
add_product('4800011122236', 'alcohol', 15)
add_product('4800135003312', 'lotion', 20)
add_product('4809010508812', 'milcu', 5)
add_product('8802203083659', 'pen', 1)
"""

#scan_barcode()

