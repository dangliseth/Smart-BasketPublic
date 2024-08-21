import pyzbar.pyzbar as pyzbar
import tkinter as tk
from PIL import Image, ImageTk
import qrcode
import firestore



def init(root):
    root = root
    root.title("Sentinels Smart Basket")

    global items
    global total    
    items = {}
    total = 0.0

    global display    
    display = tk.Text(root, height=15, width=40)
    display.pack()

    global total_label    
    total_label = tk.Label(root, text=f"Total: ₱0.00")
    total_label.pack()

    qr_button = tk.Button(root, text="Generate QR Code", command=auto_scan)
    qr_button.pack()

    #auto_scan()

def auto_scan():
    barcode = firestore.scan_barcode()
    if barcode:
        product, price = firestore.get_product_info(barcode)
        product = str(product)
        price = float(price)
        if product in items:
            items[product]['quantity'] += 1
        else:
            items[product] = {'price': price, 'quantity': 1}
        #total += price
        update_display()
        
    #root.after(1000, auto_scan)

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
        display.insert(tk.END, f"{product} - ₱{details['price']} x {details['quantity']}\n")
        
    total_label.config(text=f"Total: ₱{total:.2f}")





root = tk.Tk()
init(root)
root.mainloop()