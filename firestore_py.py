import cv2
import numpy as np
#import tensorflow as tf
from tflite_runtime.interpreter import Interpreter
import firebase_admin
from firebase_admin import credentials, firestore


import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tkb

# Initialize Firebase
cred = credentials.Certificate("smart-basket-90f82-firebase-adminsdk-jns92-99b59e40f0.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


cap = cv2.VideoCapture(0)

def load_model(model_path):
    interpreter = Interpreter(model_path)
    interpreter.allocate_tensors()
    return interpreter

interpreter = load_model('model.tflite')

# Function to preprocess the camera frame for the TFLite model
def preprocess_image(frame, input_shape):
    # Convert the frame to grayscale
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Resize the grayscale image to match the model's input size
    frame_resized = cv2.resize(frame_gray, (input_shape[1], input_shape[2]))
    
    # Expand dimensions to match the expected input shape (1, height, width, 1)
    frame_resized = np.expand_dims(frame_resized, axis=(0, -1))  # Add batch and channel dimensions
    frame_resized = frame_resized.astype(np.float32) / 255.0  # Normalize pixel values
    
    return frame_resized


# Function to run classification
def classify_frame(interpreter, input_data):
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    return interpreter.get_tensor(output_details[0]['index'])

# Function to fetch product info from Firestore
def get_product_info(label):
    product_ref = db.collection('items').document(label)
    product = product_ref.get()
    if product.exists:
        return product.to_dict()
    else:
        print(f"No product found for label: {label}")
        return None

# Function to update the display with the product information
def update_display(product_info):
    display.insert(tk.END, f"Product: {product_info['itemName']}\nPrice: {product_info['itemPrice']}\n\n")
    total_label.config(text=f"Total: {sum([items[item]['price'] * items[item]['quantity'] for item in items])}")

# Function to classify and fetch product info
def auto_scan(interpreter):
    global items
    # Simulate capturing frame from camera
    ret, frame = cap.read()
    
    if ret:
        input_data = preprocess_image(frame, interpreter.get_input_details()[0]['shape'])
        output_data = classify_frame(interpreter, input_data)
        prediction_index = np.argmax(output_data[0])
        
        # Fetch product info from Firestore using the label
        product_info = get_product_info(str(prediction_index))  # Assuming Firestore doc ID is a string
        if product_info:
            label = product_info['itemName']
            price = float(product_info['itemPrice'])
            
            # Add product to basket
            if label in items:
                items[label]['quantity'] += 1
            else:
                items[label] = {'price': price, 'quantity': 1}
            
            # Update the display
            update_display(product_info)
        
    # Schedule the next scan
    root.after(1000, auto_scan, interpreter)        

def init(root):
    root
    root.title("Sentinels Smart Basket")
    root.maxsize(800, 480)
    #root.configure(bg="#f0f0f0")

    headline_label = ttk.Label(root, text="Basket", font=("Times New Roman", 50, "bold"))
    headline_label.pack(pady=5)

    global items, total_items, total, display, total_label    
    items = {}
    total = 0.0
    total_items = 0

    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, padx=20, pady=20)


    display = tk.Text(frame, wrap=tk.WORD)
    display.grid(row=0, column=0, sticky="nsew")
  
    total_label = ttk.Label(frame, text=f"")
    total_label.grid(row=1, column=0, sticky="nsew")

    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    #qr_button = tk.Button(root, text="Generate QR Code", command=generate_qr_code)
    #qr_button.pack()

    tkb.Style().theme_use("solar")

    #scan_sample = tk.Button(root, text="Scan", command=auto_scan)
    #scan_sample.pack()

    #scan_sample1 = tk.Button(root, text="Scan", command=auto_scan1)
    #scan_sample1.pack()
    
    root.after(1000, auto_scan, interpreter)
    
if __name__ == "__main__":
    root = tk.Tk()
    init(root)
    root.mainloop()

