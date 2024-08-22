import cv2
import pyzbar.pyzbar as pyzbar

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate(
    "smart-basket-90f82-firebase-adminsdk-jns92-99b59e40f0.json"
    )
firebase_admin.initialize_app(cred)
db = firestore.client()
doc_ref = db.collection("items")

def scan_barcode():
    #cap = cv2.VideoCapture(0)  
    #ret, frame = cap.read()
    #if ret:
        #barcodes = pyzbar.decode(frame)
        #for barcode in barcodes:
            #global barcode_data
            barcode_data = "rtSK21qfunPHD9CFULuu"
            #cap.release() 
            return barcode_data
    #cap.release()  
    #return None

def get_product_info(barcode_data):
    query = doc_ref.document(barcode_data).get()

    if query.exists:
        item_data = query.to_dict()
        itemName = item_data.get("itemName")
        itemPrice = item_data.get("itemPrice")
        return itemName, itemPrice
    
    return None, None
