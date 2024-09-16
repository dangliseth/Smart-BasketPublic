import pyzbar.pyzbar as pyzbar
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tkb
from PIL import Image, ImageTk
import qrcode
import firestore_py
import camtest



def init(root):
    root
    root.title("Sentinels Smart Basket")
    root.maxsize(800, 480)
    #root.configure(bg="#f0f0f0")

    headline_label = ttk.Label(root, text="Basket", font=("Times New Roman", 50, "bold"))
    headline_label.pack(pady=5)

    global items
    global total
    global total_items      
    items = {}
    total = 0.0
    total_items = 0

    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, padx=20, pady=20)

    global display    
    display = tk.Text(frame, wrap=tk.WORD)
    display.grid(row=0, column=0, sticky="nsew")

    global total_label    
    total_label = ttk.Label(frame, text=f"")
    total_label.grid(row=1, column=0, sticky="nsew")

    frame.columnconfigure(0, weight=1)
    frame.rowconfigure(0, weight=1)

    qr_button = tk.Button(root, text="Generate QR Code", command=generate_qr_code)
    qr_button.pack()

    tkb.Style().theme_use("solar")

    #scan_sample = tk.Button(root, text="Scan", command=auto_scan)
    #scan_sample.pack()

    #scan_sample1 = tk.Button(root, text="Scan", command=auto_scan1)
    #scan_sample1.pack()
    
    root.after(1000, auto_scan)
def auto_scan():
    #barcode = firestore_py.scan_barcode()
    #if barcode:
        product, price = firestore_py.get_product_info()
        product = str(product)
        price = float(price)
        if product in items:
            items[product]['quantity'] += 1
        else:
            items[product] = {'price': price, 'quantity': 1}
        #total += price
        update_display()
    
        
    #root.after(1000, auto_scan)

#def auto_scan1():
    #barcode = firestore_py.sample()
    #if barcode:
        #product, price = firestore_py.get_product_info(barcode)
        #product = str(product)
        #price = float(price)
        #if product in items:
            #items[product]['quantity'] += 1
        #else:
            #items[product] = {'price': price, 'quantity': 1}
        #total += price
        #update_display()


def generate_qr_code():
    qr_data = ""
    for product, details in items.items():
        qr_data += f"{product}: {details['quantity']} x ₱{details['price']}\n"
    qr_data += f"\nTotal: ₱{total:.2f}"

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
    qr_label = tk.Label(root, image=qr_img_tk)
    qr_label.image = qr_img_tk
    qr_label.pack()

def update_display():
    display.delete(1.0, tk.END)
    for product, details in items.items():
        display.insert(tk.END, f"{product} - ₱{details['price']}    x{details['quantity']}\n")

 
    total_items = sum(details['quantity'] for details in items.values())
    total = sum(details['price'] * details['quantity'] for details in items.values())
    total_label.config(text=f"Total: ₱{total:.2f}               Total Items: {total_items}")




if __name__ == "__main__":
    root = tk.Tk()
    init(root)
    root.mainloop()
