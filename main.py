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

    global items, total, total_label, logoImage, budget
    items = {}
    total = 0.0
    budget = 0.0

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
    
    global button_frame
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
    
    global set_budget_button
    set_budget_button = tk.Button(button_frame, text="Set Budget", command=show_budget_entry, bd=0, fg="white", bg="#CB4949", font=("Sans-Serif", 12))
    set_budget_button.grid(row=3, column=1, columnspan=2, padx=5, pady=2)

    global budget_label_display
    # Label to display the set budget after it's confirmed
    budget_label_display = tk.Label(button_frame, text="Budget: P0.00", bg="#FFC4C4", font=("Arial", 12))
    budget_label_display.grid(row=2, column=1, sticky="nsew", columnspan=2, padx=5, pady=2)
        
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

def show_budget_entry():
    global budget_entry, keyboard_window

    # Remove the button after it's clicked
    set_budget_button.grid_forget()

    # Create a new Entry box where the button was
    budget_entry = tk.Entry(button_frame, font=("Arial", 12), width=10)
    budget_entry.grid(row=3, column=1, columnspan=2, padx=5, pady=2)

    keyboard_window = show_on_screen_keyboard(budget_entry)
    
    # Add a new button for confirming budget entry
    global confirm_budget_button
    confirm_budget_button = tk.Button(button_frame, text="Confirm", command=set_budget_from_entry, bd=0, fg="white", bg="#CB4949", font=("Sans-Serif", 12))
    confirm_budget_button.grid(row=4, column=1, columnspan=2, padx=5, pady=2)

def key_press(button_text, entry_widget):
    current_text = entry_widget.get()
    if button_text == "Clear":
        entry_widget.delete(0, tk.END)
    elif button_text == "Backspace":
        entry_widget.delete(len(current_text) - 1, tk.END)
    else:
        entry_widget.insert(tk.END, button_text)

# Function to show the numerical on-screen keyboard
def show_on_screen_keyboard(entry_widget):
    keyboard_window = tk.Toplevel()
    keyboard_window.title("On-Screen Keyboard")
    
    # Configure grid for numeric layout
    keyboard_window.geometry("300x300")
    buttons = [
        '1', '2', '3',
        '4', '5', '6',
        '7', '8', '9',
        'Clear', '0', 'Backspace'
    ]
    
    for i, button_text in enumerate(buttons):
        button = tk.Button(
            keyboard_window, text=button_text, width=8, height=2,
            command=lambda text=button_text: key_press(text, entry_widget)
        )
        button.grid(row=i//3, column=i%3, padx=5, pady=5)
    return keyboard_window

def set_budget_from_entry():
    # Get the value from the entry box
    amount = budget_entry.get()
    if keyboard_window:
        keyboard_window.destroy()

    try:
        budget = float(amount)
        budget_label_display.config(text=f"Budget: P{budget:.2f}")
        print(f"Budget set to: P{budget:.2f}")

        budget_entry.grid_forget()
        confirm_budget_button.grid_forget()

        # Show the set_budget_button again for future updates
        set_budget_button.grid(row=3, column=1, columnspan=2, padx=5, pady=2)

        # Check if the total exceeds the budget and show an alert if necessary
        if total >= budget:
            show_custom_error("Budget Alert", f"Your total of P{total:.2f} exceeds the budget of P{budget:.2f}!")
    except ValueError:
        show_custom_error("Invalid Input", "Please enter a valid number for the budget.")

    
def show_custom_error(title, message="Error occurred", image="warning.jpg"):
    # Create a new window for the error message
    error_window = tk.Toplevel()
    error_window.title(title)
    error_window.geometry("300x150")

    # Error image (optional)
    try:
        img = Image.open(image)
        img = img.resize((50, 50), Image.ANTIALIAS)
        img_tk = ImageTk.PhotoImage(img)
        image_label = tk.Label(error_window, image=img_tk)
        image_label.image = img_tk
        image_label.pack(pady=10)
    except Exception as e:
        print(f"Image load failed: {e}")
    
    # Display the error message
    error_label = tk.Label(error_window, text=message, font=("Arial", 12), wraplength=250)
    error_label.pack(pady=10)

    # OK button to close the error window
    ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
    ok_button.pack(pady=5)

    error_window.grab_set()
    
    
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