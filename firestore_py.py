import cv2

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import camtest

import easygui as e

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
            barcode_data = camtest.classification()
            if barcode_data == "3":
                barcode_data = "15235253435"
                
            barcode_data = barcode_data
            #cap.release() 
            return barcode_data
    #cap.release()  
    #return None

def sample():
       barcode_data1 = "15235253435"
       return barcode_data1

def get_product_info():
    data = camtest.classification()
    query = doc_ref.document(data).get()
    

    if query.exists:
        item_data = query.to_dict()
        itemName = item_data.get("itemName")
        itemPrice = item_data.get("itemPrice")
        return itemName, itemPrice
    
    return None, None

if __name__ == "__main__":
       e.msgbox("I'm a module :(", "Simula ka sa Main")
