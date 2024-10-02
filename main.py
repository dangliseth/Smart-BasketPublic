import tkinter as tk
from PIL import Image, ImageTk
import qrcode
import threading
import firestore_py
import time  # Import time to use for interval tracking
from pyzbar.pyzbar import decode
from firestore_py import scan_barcode
import os
import customtkinter


def init(root):
    root.title("Sentinels Smart Basket")
    root.geometry("800x480")
    root.configure(bg="#FFC4C4")
    
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=1)
    root.grid_rowconfigure(3, weight=1)


    sframe = customtkinter.CTkScrollableFrame(
        root,
        height=200,  # Adjust height
        width=350,   # Adjust width
    )
    sframe.grid(row=2, column=0, sticky="nsew", padx=25, pady=(0, 25))

    global items, total, total_label, logoImage
    items = {}
    total = 0.0

    title_frame = tk.Frame(root, bg="#FFC4C4")
    title_frame.grid(row=0, column=0, columnspan=2, sticky="nsew", padx=10)
    
    image_label = tk.Label(title_frame, bg="#FFC4C4")
    image_label.pack(side=tk.LEFT, padx=0)

    # Load the image to replace text
    logo_image = Image.open("savers.png")  # Replace 'your_image.png' with your actual image file
    logo_image = logo_image.resize((200, 50), Image.Resampling.LANCZOS)  # Resize if needed
    logo_tk = ImageTk.PhotoImage(logo_image)

    # Create an image label to replace the text
    image_label = tk.Label(title_frame, image=logo_tk, bg="#FFC4C4")
    image_label.image = logo_tk  # Keep a reference to avoid garbage collection
    image_label.pack(side=tk.LEFT, padx=0)
    
    
    bottom_frame = tk.Frame(root, bg="#FFC4C4")
    bottom_frame.grid(row=1, column=0, columnspan=2, rowspan=2, sticky="nsew")

    table_frame = tk.Frame(bottom_frame, bg="white")
    table_frame = customtkinter.CTkScrollableFrame(bottom_frame)
    table_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 20))
    table_frame.grid_columnconfigure(0, weight=1)
    table_frame.grid_columnconfigure(1, weight=1)
    table_frame.grid_columnconfigure(2, weight=1)
    table_frame.config(bg="#F0F0F0")

    tk.Label(table_frame, text="All Items", bg="#F0F0F0", font=("Arial", 12)).grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=(8, 5))
    tk.Label(table_frame, text="Price", bg="#F0F0F0", font=("Arial", 12)).grid(row=0, column=1, sticky="nsew", padx=(45, 0), pady=(8, 5))
    tk.Label(table_frame, text="Quantity", bg="#F0F0F0", font=("Arial", 12)).grid(row=0, column=2, sticky="nsew", padx=(5, 12), pady=(8, 5))
    
    underline_frame = tk.Frame(table_frame, height=2, bg="black")
    underline_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(0, 10), padx=8)

    global rows_frame
    rows_frame = tk.Frame(table_frame, bg="#F0F0F0")
    rows_frame.grid(row=2, column=0, columnspan=3, sticky="nsew")
    rows_frame.grid_rowconfigure(0, weight=1)
    rows_frame.grid_columnconfigure(0, weight=1)
    rows_frame.grid_columnconfigure(1, weight=1)
    rows_frame.grid_columnconfigure(2, weight=1)
    
    button_frame = tk.Frame(bottom_frame, bg="#FFC4C4")
    button_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
    
    button_frame.grid_rowconfigure(0, weight=1)
    button_frame.grid_rowconfigure(1, weight=1)
    button_frame.grid_rowconfigure(2, weight=1)
    button_frame.grid_rowconfigure(3, weight=1)
    button_frame.grid_rowconfigure(4, weight=1)
    button_frame.grid_rowconfigure(5, weight=1)
    button_frame.grid_rowconfigure(6, weight=1)
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=2)
    button_frame.grid_columnconfigure(2, weight=1)
    
    #scan_sample = tk.Button(button_frame, text="Scan", command=auto_scan, bd=0, fg="white", bg="#CB4949", font=("Sans-Serif", 12))
    #scan_sample.grid(row=4, column=1, sticky="nsew", columnspan=2, padx=5, pady=2)

    qr_button = tk.Button(button_frame, text="Checkout", command=checkout, bd=0, fg="white", bg="#CB4949", font=("Sans-Serif", 12), padx=10, pady=8)
    qr_button.grid(row=6, column=1, sticky="new", columnspan=2, padx=5, pady=2)

    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=3)
    root.grid_columnconfigure(0, weight=2)
    root.grid_columnconfigure(1, weight=1)

    bottom_frame.grid_rowconfigure(0, weight=1)
    bottom_frame.grid_columnconfigure(0, weight=2)
    bottom_frame.grid_columnconfigure(1, weight=1)
    
    global total_label
    total_label = tk.Label(button_frame, text=f"₱0.00  ", bg="#FFC4C4", font=("Arial", 12), highlightbackground="#CB4949", highlightthickness=2)
    total_label.grid(row=5, column=1, sticky="nsew", columnspan=2, padx=5, pady=2)
    
    root.after(2000, auto_scan())

def auto_scan():
    def update_display_from_scan(product, tag):
        if product:
            print(f"Product fetched: {product}")
            name = product['itemName']
            price = float(product['itemPrice'])
            
            # Create a unique key for the item using its name and the RFID tag
            unique_key = f"{name}_{tag}"
            
            # Check if the item is already in the 'items' dictionary
            if unique_key in items:
                # Item exists, remove it
                items[unique_key]['quantity'] -= 1
                if items[unique_key]['quantity'] <= 0:
                    del items[unique_key]  # Remove item from the dictionary if quantity is 0
                print(f"Removed item: {name}. Remaining quantity: {sum(item['quantity'] for item in items.values() if item['itemName'] == name)}")
            else:
                # Item doesn't exist, add it
                items[unique_key] = {'price': price, 'quantity': 1, 'itemName': name}  # Store itemName for display
                print(f"Added item: {name}. Quantity: {sum(item['quantity'] for item in items.values() if item['itemName'] == name)}")

            aggregate_items = {}
            for key, details in items.items():
                item_name = details['itemName']
                if item_name not in aggregate_items:
                    aggregate_items[item_name] = {'price': details['price'], 'quantity': details['quantity']}
                else:
                    aggregate_items[item_name]['quantity'] += details['quantity']

            # Update the display using the aggregated item names and quantities
            update_display(aggregate_items)
        else:
            print("Product not found in the database.")
    
    # Start barcode scanning in a separate thread
    scanning_thread = threading.Thread(target=scan_barcode, args=(update_display_from_scan,))
    scanning_thread.daemon = True
    scanning_thread.start()
    
    
def show_custom_error(title, image = 'warning.jpg'):
    # Create a new window for the error message
    error_window = tk.Toplevel()
    error_window.title(title)
    error_window.geometry("300x150")
    
    # Load the custom 'X' image
    try:
        img = Image.open(image)  # Replace with your image path
        img = img.resize((50, 50), Image.ANTIALIAS)  # Resize the image if necessary
        img_tk = ImageTk.PhotoImage(img)
        
        # Create an image label and pack it into the error window
        image_label = tk.Label(error_window, image=img_tk)
        image_label.image = img_tk  # Keep a reference to avoid garbage collection
        image_label.pack(pady=10)
    except Exception as e:
        print(f"Error loading image: {e}")
    
    # Create a label for the error message and pack it
    message_label = tk.Label(error_window, text="Unrecognized barcode! Please try again.")
    message_label.pack(pady=5)
    
    # Auto-close the error window after 2 seconds (2000 milliseconds)
    error_window.after(1000, error_window.destroy)
    
    # Keep the error window on top
    error_window.transient()
    error_window.grab_set()
    error_window.mainloop()
    
    
def reset_basket():
    global items, total
    items = {}
    total = 0.0
    update_display()

def checkout():
    qr_data = ""
    for product, details in items.items():
        qr_data += f"{product}: {details['quantity']} x ₱{details['price']:.2f}\n"
    qr_data += f"\nTotal: ₱{total:.2f}"

    print("QR Code Data:", qr_data)  # Debugging line

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    qr_img = qr.make_image(fill='black', back_color='white')
    qr_img.save("basket_qr.png")

    qr_img_tk = ImageTk.PhotoImage(Image.open("basket_qr.png"))

    qr_window = tk.Toplevel(root)
    qr_window.title("QR Code")

    qr_label = tk.Label(qr_window, image=qr_img_tk)
    qr_label.image = qr_img_tk
    qr_label.pack()

    # Finish Shopping button
    finish_button = tk.Button(qr_window, text="Finish Shopping", command=reset_basket, bd=0, fg="white", bg="#CB4949", font=("Sans-Serif", 12), padx=10, pady=8)
    finish_button.pack(pady=10)

    def close_qr_window():
        qr_window.destroy()

    # Automatically close the QR code window after 5 seconds (adjust as needed)
    qr_window.after(10000, close_qr_window)

    qr_window.grab_set()  # Make the QR code window modal



IMAGE_PATH = "items"

def update_display(aggregate_items):
    for widget in rows_frame.winfo_children():
        widget.destroy()

    row_number = 0
    for name, details in aggregate_items.items():
        quantity = details['quantity']
        price = details['price']
        # Create an inner frame for the product image and name
        product_frame = tk.Frame(rows_frame, bg="#F0F0F0")
        product_frame.grid(row=row_number, column=0, sticky="nsew", padx=5)

        # Image and text frame
        image_text_frame = tk.Frame(product_frame, bg="#F0F0F0")
        image_text_frame.pack(side=tk.LEFT, padx=5, pady=5)

        # Load the item image
        image_file = os.path.join(IMAGE_PATH, f"{name}.png")
        print(f"Loading image from: {image_file}")  # Debugging line
        
        if os.path.exists(image_file):
            item_image = Image.open(image_file)
            item_image = item_image.resize((50, 50), Image.Resampling.LANCZOS)  # Resize if needed
            item_image_tk = ImageTk.PhotoImage(item_image)
            image_label = tk.Label(image_text_frame, image=item_image_tk, bg="#F0F0F0")
            image_label.image = item_image_tk  # Keep a reference to avoid garbage collection
            image_label.pack(side=tk.LEFT, padx=5)
        else:
            # If image not found, show a placeholder or empty label
            image_label = tk.Label(image_text_frame, text="No Image", bg="#F0F0F0")
            image_label.pack(side=tk.LEFT, padx=5)

        # Product name
        name_label = tk.Label(image_text_frame, text=name, bg="#F0F0F0")
        name_label.pack(side=tk.LEFT, padx=5)

        # Price
        tk.Label(rows_frame, text=f"₱{price:.2f}", bg="#F0F0F0").grid(row=row_number, column=1, sticky="nsew")

        # Quantity
        quantity_label = tk.Label(rows_frame, text=f"{quantity}", bg="#F0F0F0")
        quantity_label.grid(row=row_number, column=2, sticky="nsew")
        
        # Minus button
        #minus_button = tk.Button(rows_frame, text="—", command=lambda p=product: decrement_quantity(p), bg="#F0F0F0", fg="#CB4949", bd=0, font=("Arial", 10))
        #minus_button.grid(row=row_number, column=3, sticky="nse", padx=(0,20), pady=(0,5))

        # Underline
        underline_frame = tk.Frame(rows_frame, height=1, bg="black", pady=2)
        underline_frame.grid(row=row_number + 1, column=0, columnspan=5, sticky="ew", padx=10, pady=(0, 10))

        row_number += 2

    global total
    total = sum(details['price'] * details['quantity'] for details in items.values())
    total_label.config(text=f"₱{total:.2f}")
    total_label.grid(row=5, column=1, sticky="nsew", columnspan=2, padx=5, pady=2)
    total_label.config(bg="#FFC8C8", highlightbackground="#CB4949", font=("Arial", 12), highlightthickness=2)

def decrement_quantity(product):
    if product in items:
        if items[product]['quantity'] > 1:
            items[product]['quantity'] -= 1
        else:
            del items[product]
        update_display()

root = tk.Tk()
init(root)
root.mainloop()