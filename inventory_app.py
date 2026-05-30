import tkinter as tk
from tkinter import ttk, messagebox
import json
import os

FILE_NAME = "inventory.json"


class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("מערכת ניהול מלאי")
        self.root.geometry("900x500")

        self.inventory = self.load_inventory()

        self.create_widgets()
        self.refresh_table()

    def load_inventory(self):
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, "r", encoding="utf-8") as file:
                return json.load(file)
        return []

    def save_inventory(self):
        with open(FILE_NAME, "w", encoding="utf-8") as file:
            json.dump(self.inventory, file, ensure_ascii=False, indent=4)

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Label(frame, text="מק״ט").grid(row=0, column=0)
        self.sku_entry = tk.Entry(frame)
        self.sku_entry.grid(row=1, column=0, padx=5)

        tk.Label(frame, text="שם מוצר").grid(row=0, column=1)
        self.name_entry = tk.Entry(frame)
        self.name_entry.grid(row=1, column=1, padx=5)

        tk.Label(frame, text="כמות").grid(row=0, column=2)
        self.quantity_entry = tk.Entry(frame)
        self.quantity_entry.grid(row=1, column=2, padx=5)

        tk.Label(frame, text="מחיר").grid(row=0, column=3)
        self.price_entry = tk.Entry(frame)
        self.price_entry.grid(row=1, column=3, padx=5)

        tk.Button(frame, text="הוסף מוצר", command=self.add_product).grid(row=1, column=4, padx=5)
        tk.Button(frame, text="עדכן מוצר", command=self.update_product).grid(row=1, column=5, padx=5)
        tk.Button(frame, text="מחק מוצר", command=self.delete_product).grid(row=1, column=6, padx=5)

        search_frame = tk.Frame(self.root)
        search_frame.pack(pady=5)

        tk.Label(search_frame, text="חיפוש").pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(search_frame, text="חפש", command=self.search_product).pack(side=tk.LEFT)
        tk.Button(search_frame, text="הצג הכל", command=self.refresh_table).pack(side=tk.LEFT, padx=5)

        self.table = ttk.Treeview(
            self.root,
            columns=("sku", "name", "quantity", "price"),
            show="headings"
        )

        self.table.heading("sku", text="מק״ט")
        self.table.heading("name", text="שם מוצר")
        self.table.heading("quantity", text="כמות")
        self.table.heading("price", text="מחיר")

        self.table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.table.bind("<<TreeviewSelect>>", self.fill_fields)

    def add_product(self):
        sku = self.sku_entry.get().strip()
        name = self.name_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        price = self.price_entry.get().strip()

        if not sku or not name or not quantity or not price:
            messagebox.showerror("שגיאה", "נא למלא את כל השדות")
            return

        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            messagebox.showerror("שגיאה", "כמות חייבת להיות מספר ומחיר חייב להיות מספר")
            return

        self.inventory.append({
            "sku": sku,
            "name": name,
            "quantity": quantity,
            "price": price
        })

        self.save_inventory()
        self.refresh_table()
        self.clear_fields()

    def update_product(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showerror("שגיאה", "נא לבחור מוצר לעדכון")
            return

        index = int(selected[0])

        try:
            self.inventory[index]["sku"] = self.sku_entry.get().strip()
            self.inventory[index]["name"] = self.name_entry.get().strip()
            self.inventory[index]["quantity"] = int(self.quantity_entry.get().strip())
            self.inventory[index]["price"] = float(self.price_entry.get().strip())
        except ValueError:
            messagebox.showerror("שגיאה", "כמות ומחיר חייבים להיות מספרים")
            return

        self.save_inventory()
        self.refresh_table()
        self.clear_fields()

    def delete_product(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showerror("שגיאה", "נא לבחור מוצר למחיקה")
            return

        index = int(selected[0])
        del self.inventory[index]

        self.save_inventory()
        self.refresh_table()
        self.clear_fields()

    def search_product(self):
        search_text = self.search_entry.get().strip().lower()

        results = [
            product for product in self.inventory
            if search_text in product.get("name", "").lower()
            or search_text in product.get("sku", "").lower()
        ]

        self.refresh_table(results)

    def refresh_table(self, data=None):
        for row in self.table.get_children():
            self.table.delete(row)

        data = data if data is not None else self.inventory

        for index, product in enumerate(data):
            self.table.insert(
                "",
                tk.END,
                iid=index,
                values=(
                    product.get("sku", ""),
                    product.get("name", ""),
                    product.get("quantity", ""),
                    product.get("price", "")
                )
            )

    def fill_fields(self, event):
        selected = self.table.selection()

        if selected:
            values = self.table.item(selected[0], "values")

            self.sku_entry.delete(0, tk.END)
            self.sku_entry.insert(0, values[0])

            self.name_entry.delete(0, tk.END)
            self.name_entry.insert(0, values[1])

            self.quantity_entry.delete(0, tk.END)
            self.quantity_entry.insert(0, values[2])

            self.price_entry.delete(0, tk.END)
            self.price_entry.insert(0, values[3])

    def clear_fields(self):
        self.sku_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)


root = tk.Tk()
app = InventoryApp(root)
root.mainloop()