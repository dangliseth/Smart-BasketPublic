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


def draw_gradient(canvas, width, height, color1, color2):
    """Draw a horizontal gradient rectangle on the canvas."""
    for i in range(width):
        ratio = i / width
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        color = f'#{r:02x}{g:02x}{b:02x}'
        canvas.create_line(i, 0, i, height, fill=color)  # Draw vertical line for the gradient

def init(root):
    root.title("Sentinels Smart Basket")
    root.geometry("800x480")
    root.configure(bg="#FFF6E8")
    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=1)
    root.grid_rowconfigure(3, weight=1)
    root.grid_rowconfigure(4, weight=1)
    root.grid_rowconfigure(5, weight=1)
    root.grid_rowconfigure(6, weight=1)
    root.grid_rowconfigure(7, weight=1)
    root.grid_rowconfigure(8, weight=1)
    root.grid_rowconfigure(9, weight=1)

    global items, total, total_label, total_item_count, budget, total_value, vat_value, subtotal_value
    items = {}
    subtotal_value = 0.0
    vat_value = 0.0
    total = 0.0
    total_value = 0.0
    budget = 0.0
    total_item_count = 0 

    title_frame = tk.Frame(root, bg="#FFF6E8")
    title_frame.grid(row=0, column=0, columnspan=2, sticky="sew", padx=10)

    image_label = tk.Label(title_frame, bg="#FFF6E8")
    image_label.pack(side=tk.LEFT, padx=0)

    # Load the logo image
    logo_image = Image.open("savers.png")
    logo_image = logo_image.resize((200, 50), Image.Resampling.LANCZOS)
    logo_tk = ImageTk.PhotoImage(logo_image)

    # Create an image label for the logo
    image_label = tk.Label(title_frame, image=logo_tk, bg="#FFF6E8")
    image_label.image = logo_tk  # Keep a reference to avoid garbage collection
    image_label.pack(side=tk.LEFT, padx=0)

    # Middle Frame for Shopping Basket label
    middle_frame = tk.Frame(root, bg="#FFD4D4", height=25)
    middle_frame.grid(row=1, column=0, columnspan=2, sticky="sew", padx=10)
    middle_frame.columnconfigure(0, weight=1)
    middle_frame.columnconfigure(1, weight=1)

    # Left Middle Frame
    left_middle_frame = tk.Frame(middle_frame, bg="#FFF6E8")
    left_middle_frame.grid(row=0, column=0, sticky="nsew", columnspan=1)

    # Right Middle Frame
    right_middle_frame = tk.Frame(middle_frame, bg="#FFF6E8")
    right_middle_frame.grid(row=0, column=1, sticky="nsew", columnspan=1)
    right_middle_frame.grid_columnconfigure(0, weight=1)
    right_middle_frame.grid_columnconfigure(1, weight=1)
    right_middle_frame.grid_columnconfigure(2, weight=1)
    right_middle_frame.grid_columnconfigure(3, weight=1)
    right_middle_frame.grid_columnconfigure(4, weight=1)
    right_middle_frame.grid_columnconfigure(5, weight=1)
    right_middle_frame.grid_columnconfigure(6, weight=1)
    right_middle_frame.grid_rowconfigure(0, weight=1)

    inside_right_middle_frame = tk.Frame(right_middle_frame, highlightthickness=2, highlightbackground="#FFA4A4",
                                         highlightcolor="#FFA4A4")
    inside_right_middle_frame.grid(sticky="nsew", row=0, column=5, columnspan=1, rowspan=2)
    inside_right_middle_frame.grid_columnconfigure(0, weight=1)
    inside_right_middle_frame.grid_columnconfigure(1, weight=1)
    inside_right_middle_frame.grid_rowconfigure(0, weight=1)

    left_insideMiddleFrame = tk.Frame(inside_right_middle_frame, bg="#FFD4D4")
    left_insideMiddleFrame.grid(sticky="nsew", row=0, column=0)
    left_insideMiddleFrame.grid_rowconfigure(0, weight=1)
    left_insideMiddleFrame.grid_columnconfigure(0, weight=1)

    right_insideMiddleFrame = tk.Frame(inside_right_middle_frame, bg="#FFD4D4")
    right_insideMiddleFrame.grid(sticky="nsew", row=0, column=1)
    right_insideMiddleFrame.grid_rowconfigure(0, weight=1)
    right_insideMiddleFrame.grid_columnconfigure(1, weight=1)

    shopping_title = tk.Label(left_middle_frame, text="Shopping Basket", bg="#FFF6E8", font=("Arial bold", 25))
    shopping_title.grid(pady=5, sticky="w")  # Add some padding for spacing

    global budget_label_display
    # Optional: Add a label above the entry field for clarity
    budget_label_display = tk.Label(left_insideMiddleFrame, text="Budget:", bg="#FFD4D4", font=("Arial bold", 12))
    budget_label_display.grid(row=0, column=0, sticky="nsew")

    global set_budget_button
    set_budget_button = tk.Button(right_insideMiddleFrame, text="Set Budget", command=show_budget_entry, bd=0, fg="white", bg="#CB4949", font=("Sans-Serif", 12))
    set_budget_button.grid(row=0, column=0, columnspan=2, sticky="ew", padx=5, pady=2)  # Adjust columnspan and sticky


    # Create a canvas for the gradient line
    gradient_canvas = tk.Canvas(left_middle_frame, height=7, bg="#FFF6E8", highlightthickness=0)
    gradient_canvas.grid()  # Fill the width
    # Draw the gradient line from dark red to white
    draw_gradient(gradient_canvas, 390, 7, (171, 40, 40), (255, 255, 255))  # Dark red to white

    # Bottom Frame (table frame)
    bottom_frame = tk.Frame(root, bg="#FFF6E8")
    bottom_frame.grid(row=2, column=0, columnspan=2, rowspan=8, sticky="nsew", )
    bottom_frame.grid_columnconfigure(0, weight=1)
    bottom_frame.grid_columnconfigure(1, weight=1)
    bottom_frame.grid_columnconfigure(2, weight=1)

    bottom_frame.grid_rowconfigure(0, weight=1)

    # bottom_frame.grid_rowconfigure(0, weight=1)
    # bottom_frame.grid_columnconfigure(0, weight=1)
    # bottom_frame.grid_columnconfigure(1, weight=1)

    table_frame = customtkinter.CTkScrollableFrame(bottom_frame, fg_color="#F6DAD1", border_color="#A30A0A",
                                                   border_width=2, scrollbar_button_color="#A30A0A")
    table_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 20))
    table_frame.grid_columnconfigure(0, weight=1)
    table_frame.grid_columnconfigure(1, weight=1)
    table_frame.grid_columnconfigure(2, weight=1)
    table_frame.grid(columnspan=2, rowspan=9)

    tk.Label(table_frame, text="Product", bg="#F6DAD1", fg="#FF6969", font=("Arial bold", 14)).grid(row=0, column=0,
                                                                                                    sticky="nsw",
                                                                                                    padx=(10, 5))
    tk.Label(table_frame, text="Price", bg="#F6DAD1", fg="#FF6969", font=("Arial bold", 14)).grid(row=0, column=1,
                                                                                                  sticky="nsew",
                                                                                                  padx=(45, 0))
    tk.Label(table_frame, text="Quantity", bg="#F6DAD1", fg="#FF6969", font=("Arial bold", 14)).grid(row=0, column=2,
                                                                                                     sticky="nse",
                                                                                                     padx=(5, 12))
    global rows_frame
    rows_frame = tk.Frame(table_frame, bg="#F0F0F0")
    rows_frame.grid(row=2, column=0, columnspan=3, sticky="nsew")
    rows_frame.grid_rowconfigure(0, weight=1)
    rows_frame.grid_columnconfigure(0, weight=1)
    rows_frame.grid_columnconfigure(1, weight=1)
    rows_frame.grid_columnconfigure(2, weight=1)

    global button_frame
    button_frame = tk.Frame(bottom_frame, bg="#FFF6E8")
    button_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10, columnspan=2)

    button_frame.grid_rowconfigure(0, weight=1)
    button_frame.grid_rowconfigure(1, weight=1)
    button_frame.grid_rowconfigure(2, weight=1)
    button_frame.grid_rowconfigure(3, weight=1)
    button_frame.grid_rowconfigure(4, weight=1)
    button_frame.grid_rowconfigure(5, weight=1)
    button_frame.grid_rowconfigure(6, weight=1)
    button_frame.grid_rowconfigure(7, weight=1)
    button_frame.grid_rowconfigure(8, weight=1)
    button_frame.grid_rowconfigure(9, weight=1)

    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=2)
    button_frame.grid_columnconfigure(2, weight=1)
    button_frame.grid_columnconfigure(3, weight=1)

    global upper_button_frame
    upper_button_frame = tk.Frame(button_frame, bg="#FFD4D4", highlightbackground="#FFA4A4", highlightcolor="#FFA4A4",
                                  highlightthickness=2, padx=5, pady=5)
    upper_button_frame.grid(row=1, column=1, rowspan=6, columnspan=8, sticky="nsew", padx=5, pady=5)

    global lower_button_frame
    lower_button_frame = tk.Frame(button_frame, bg="#FFF6E8")
    lower_button_frame.grid(row=7, column=1, rowspan=6, columnspan=8, sticky="nsew", padx=5, pady=5)

    upper_button_frame.grid_rowconfigure(0, weight=1)
    upper_button_frame.grid_rowconfigure(1, weight=1)
    upper_button_frame.grid_rowconfigure(2, weight=1)
    upper_button_frame.grid_rowconfigure(3, weight=1)
    upper_button_frame.grid_rowconfigure(4, weight=1)
    upper_button_frame.grid_rowconfigure(5, weight=1)
    upper_button_frame.grid_rowconfigure(6, weight=1)
    upper_button_frame.grid_rowconfigure(7, weight=1)
    upper_button_frame.grid_rowconfigure(8, weight=1)
    upper_button_frame.grid_rowconfigure(9, weight=1)
    upper_button_frame.grid_rowconfigure(10, weight=1)

    upper_button_frame.grid_columnconfigure(0, weight=1)
    upper_button_frame.grid_columnconfigure(1, weight=1)

    lower_button_frame.grid_rowconfigure(0, weight=1)
    lower_button_frame.grid_rowconfigure(1, weight=1)
    lower_button_frame.grid_rowconfigure(2, weight=1)
    lower_button_frame.grid_columnconfigure(0, weight=1)
    lower_button_frame.grid_columnconfigure(1, weight=1)
    lower_button_frame.grid_columnconfigure(2, weight=1)
    lower_button_frame.grid_columnconfigure(3, weight=1)

    #basket_image = Image.open("basket.png")  # Ensure the image file path is correct
    #basket_image = basket_image.resize((35, 35))  # Resize image if needed
    #basket_photo = ImageTk.PhotoImage(basket_image)

    total_items_frame = tk.Label(lower_button_frame, text="Total Items:", highlightbackground="#FFA4A4", highlightthickness=2,
                                 bg="#FFD4D4",
                                 font=("Arial bold", 10))
    total_items_frame.grid(row=1, column=1, columnspan=2, sticky="nsew", rowspan=1)

    global summary_label
    summary_label = tk.Label(upper_button_frame, text="Summary", font=("Arial bold", 16), bg="#FFD4D4")
    summary_label.grid(row=0, column=0, columnspan=2, sticky="nsw", padx=5, pady=10)

    underline_frame = tk.Frame(upper_button_frame, height=3, bg="#AB2828")
    underline_frame.grid(row=1, column=0, columnspan=2, sticky="new", padx=5)

    subtotal_label = tk.Label(upper_button_frame, text="Subtotal", font=("Arial bold", 12), bg="#FFD4D4")
    subtotal_label.grid(row=2, column=0, columnspan=2, sticky="nw", padx=(9, 0))

    subtotal_data = tk.Label(upper_button_frame, text="", font=("Arial bold", 10), bg="#FFD4D4")
    subtotal_data.grid(row=0, column=0, sticky="e", padx=10)

    vat_label = tk.Label(upper_button_frame, text="VAT (12%)", font=("Arial bold", 10), bg="#FFD4D4")
    vat_label.grid(row=3, column=0, columnspan=2, sticky="nw", padx=(10, 0))

    vat_data = tk.Label(upper_button_frame, text="", font=("Arial bold", 10), bg="#FFD4D4")
    vat_data.grid(row=3, column=1, sticky="nse", padx=(0, 9))

    underline_frame = tk.Frame(upper_button_frame, height=1, bg="#A30A0A")
    underline_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=5)

    total_label = tk.Label(upper_button_frame, text="Order Total", font=("Arial bold", 10), bg="#FFD4D4")
    total_label.grid(row=5, column=0, columnspan=2, sticky="nw", padx=(9, 0))

    total_data = tk.Label(upper_button_frame, text="", font=("Arial bold", 10), bg="#FFD4D4")
    total_data.grid(row=5, column=1, sticky="nse", padx=(0, 9))


    qr_button = tk.Button(upper_button_frame, text="GENERATE QR CODE", command=checkout,
                         bd=0, fg="black", bg="#FFFFFF", highlightthickness=2, highlightbackground="#FF6969",
                         font=("Arial bold", 8), pady=2, padx=10)
    qr_button.grid(row=7, column=0, sticky="ns", columnspan=2, rowspan=2)

    def update_item_count():
     global total_item_count
     total_item_count = sum(quantity for _, _, quantity in items)  # Calculate total item count
     total_items_frame.config(text=f"{total_item_count} Item{'s' if total_item_count != 1 else ''}")  # Update label

    def update_totals():
     global subtotal, vat, total
     subtotal = sum(price * quantity for _, price, quantity in items)
     vat = subtotal * 0.15  # Assuming VAT is 15%
     total = subtotal + vat
     display_totals()

    def display_totals():
     # Configure labels for right alignment
     subtotal_label.config(text=f"Subtotal: ₱{subtotal:.2f}")
     vat_label.config(text=f"VAT (12%): ₱{vat:.2f}")
     total_label.config(text=f"Order Total: ₱{total:.2f}")
     subtotal_label.pack(side='top', anchor='e', padx=10)
     vat_label.pack(side='top', anchor='e', padx=10)
     total_label.pack(side='top', anchor='e', padx=10)

 
    # Function to add an item and update totals
    def add_item(price):
     global subtotal_value, vat_value, total_value
     subtotal_value += price
     vat_value = subtotal_value * 0.12  # Recalculate VAT
     total_value = subtotal_value + vat_value  # Recalculate total
    update_totals()  # Update the displayed totals


    root.grid_rowconfigure(0, weight=1)
    root.grid_rowconfigure(1, weight=3)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)



def show_budget_entry():
    global budget_entry, keyboard_window

    # Create a new Entry box
    budget_entry = tk.Entry(font=("Arial", 12), width=10)
    # Show the on-screen keyboard and pass the entry widget
    keyboard_window = show_on_screen_keyboard(budget_entry)

def key_press(button_text, entry_widget):
    current_text = entry_widget.get()
    if button_text == "Clear":
        entry_widget.delete(0, tk.END)
    elif button_text == "Backspace":
        entry_widget.delete(len(current_text) - 1, tk.END)
    else:
        entry_widget.insert(tk.END, button_text)

# Global variable declarations at the top
global budget_entry, keyboard_window, confirm_button

# Function to show the numerical on-screen keyboard
def show_on_screen_keyboard(entry_widget):
    global confirm_button  # Declare confirm_button as global

    keyboard_window = tk.Toplevel()
    keyboard_window.title("On-Screen Keyboard")
    
    # Configure grid for numeric layout
    keyboard_window.geometry("300x300")
    
    # Create buttons in a grid
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
        # Place the button in a grid
        button.grid(row=i // 3, column=i % 3, padx=5, pady=5)

    # Add Confirm button at the bottom
    confirm_button = tk.Button(
        keyboard_window,
        text="Confirm",
        command=lambda: set_budget_from_entry(entry_widget),  # Pass the entry_widget directly
        bd=0,
        fg="white",
        bg="#CB4949",
        font=("Sans-Serif", 12)
    )
    confirm_button.grid(row=4, column=0, columnspan=3, padx=10, pady=10)  # Centered

    return keyboard_window

def set_budget_from_entry(entry_widget):
    global budget
    amount = entry_widget.get()

    try:
        budget = float(amount)
        budget_label_display.config(text=f"Budget: ₱{budget:.2f}")
        print(f"Budget set to: ₱{budget:.2f}")

        # Close keyboard window
        if keyboard_window:
            keyboard_window.destroy()
        
        # Reset input entry
        entry_widget.delete(0, tk.END)

        # Check if the total exceeds the budget and show an alert if necessary
        if total > budget:
            show_custom_error("Budget Alert", f"Your total of ₱{total:.2f} exceeds the budget of ₱{budget:.2f}. Please adjust your cart.")
    except ValueError:
        show_custom_error("Input Error", "Please enter a valid number.")
    
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
     finish_button = tk.Button(qr_window, text="Finish Shopping", bd=0, fg="white", bg="#CB4949", font=("Sans-Serif", 12), padx=10, pady=8)
     finish_button.pack(pady=10)

     qr_window.grab_set()  # Make the QR code window modal


IMAGE_PATH = "items"
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
