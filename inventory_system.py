import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
import pandas as pd

FILE_NAME = "inventory.json"
CATALOG_FILE = "items_catalog.xlsx"


class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("מערכת ניהול מלאי רגיש - חוסר אסור")
        self.root.geometry("1150x650")

        self.inventory = self.load_inventory()

        self.create_widgets()
        self.refresh_table()
        self.update_catalog_excel()

    def load_inventory(self):
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, "r", encoding="utf-8") as file:
                return json.load(file)
        return []

    def save_inventory(self):
        with open(FILE_NAME, "w", encoding="utf-8") as file:
            json.dump(self.inventory, file, ensure_ascii=False, indent=4)

        self.update_catalog_excel()
    def update_catalog_excel(self):
        catalog = []

        for product in self.inventory:
            catalog.append({
                "מק״ט": product.get("sku", ""),
                "שם פריט": product.get("name", ""),
                "כמות נוכחית": product.get("quantity", 0),
                "כמות מינימום": product.get("min_quantity", 1),
                "סטטוס": self.get_status(product)
            })

        df = pd.DataFrame(catalog)

        if not df.empty:
            df = df.drop_duplicates(subset=["מק״ט"])

        try:
            df.to_excel(CATALOG_FILE, index=False)
        except PermissionError:
            messagebox.showwarning(
                "קובץ Excel פתוח",
                "לא ניתן לעדכן את קובץ המקרא כי הוא פתוח כרגע.\nסגרי את items_catalog.xlsx ונסי שוב."
            )
        

    def get_status(self, product):
        quantity = product.get("quantity", 0)
        min_quantity = product.get("min_quantity", 1)

        if quantity == 0:
            return "חוסר חמור - אסור"
        elif quantity < min_quantity:
            return "התראה - מתחת למינימום"
        else:
            return "תקין"

    def create_widgets(self):
        title = tk.Label(
            self.root,
            text="מערכת ניהול מלאי רגיש - חוסר אסור",
            font=("Arial", 22, "bold"),
            fg="red"
        )
        title.pack(pady=10)

        warning = tk.Label(
            self.root,
            text="⚠️ שים לב: מדובר במלאי רגיש. אין לאפשר חוסר בפריטים. כל ירידה מתחת למינימום תסומן כהתראה.",
            font=("Arial", 12, "bold"),
            fg="red"
        )
        warning.pack(pady=5)

        form_frame = tk.LabelFrame(self.root, text="פרטי מוצר", padx=10, pady=10)
        form_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(form_frame, text="מק״ט").grid(row=0, column=0)
        self.sku_entry = tk.Entry(form_frame, width=18)
        self.sku_entry.grid(row=1, column=0, padx=5)

        tk.Label(form_frame, text="שם מוצר").grid(row=0, column=1)
        self.name_entry = tk.Entry(form_frame, width=22)
        self.name_entry.grid(row=1, column=1, padx=5)

        tk.Label(form_frame, text="כמות נוכחית").grid(row=0, column=2)
        self.quantity_entry = tk.Entry(form_frame, width=14)
        self.quantity_entry.grid(row=1, column=2, padx=5)

        tk.Label(form_frame, text="כמות מינימום").grid(row=0, column=3)
        self.min_quantity_entry = tk.Entry(form_frame, width=14)
        self.min_quantity_entry.grid(row=1, column=3, padx=5)

        tk.Label(form_frame, text="מחיר").grid(row=0, column=4)
        self.price_entry = tk.Entry(form_frame, width=14)
        self.price_entry.grid(row=1, column=4, padx=5)

        tk.Button(form_frame, text="הוסף מוצר", command=self.add_product, width=14).grid(row=1, column=5, padx=5)
        tk.Button(form_frame, text="עדכן מוצר", command=self.update_product, width=14).grid(row=1, column=6, padx=5)
        tk.Button(form_frame, text="מחק מוצר", command=self.delete_product, width=14).grid(row=1, column=7, padx=5)
        tk.Button(form_frame, text="נקה שדות", command=self.clear_fields, width=14).grid(row=1, column=8, padx=5)

        search_frame = tk.LabelFrame(self.root, text="חיפוש ופעולות", padx=10, pady=10)
        search_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(search_frame, text="חיפוש לפי שם מוצר או מק״ט").pack(side=tk.LEFT)

        self.search_entry = tk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        tk.Button(search_frame, text="חפש", command=self.search_product, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="הצג הכל", command=self.refresh_table, width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="פתח Excel", command=self.open_catalog_file, width=14).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="הצג חוסרים", command=self.show_shortages, width=14).pack(side=tk.LEFT, padx=5)

        columns = ("sku", "name", "quantity", "min_quantity", "price", "total", "status")

        self.table = ttk.Treeview(self.root, columns=columns, show="headings")

        self.table.heading("sku", text="מק״ט")
        self.table.heading("name", text="שם מוצר")
        self.table.heading("quantity", text="כמות")
        self.table.heading("min_quantity", text="מינימום")
        self.table.heading("price", text="מחיר")
        self.table.heading("total", text="שווי כולל")
        self.table.heading("status", text="סטטוס")

        self.table.column("sku", width=130, anchor=tk.CENTER)
        self.table.column("name", width=220, anchor=tk.CENTER)
        self.table.column("quantity", width=90, anchor=tk.CENTER)
        self.table.column("min_quantity", width=90, anchor=tk.CENTER)
        self.table.column("price", width=90, anchor=tk.CENTER)
        self.table.column("total", width=100, anchor=tk.CENTER)
        self.table.column("status", width=220, anchor=tk.CENTER)

        self.table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.table.bind("<<TreeviewSelect>>", self.fill_fields)

        self.table.tag_configure("critical", background="#ffb3b3")
        self.table.tag_configure("warning", background="#fff2b3")
        self.table.tag_configure("ok", background="#d9ffd9")

        self.status_label = tk.Label(self.root, text="", font=("Arial", 12, "bold"))
        self.status_label.pack(pady=5)

    def sku_exists(self, sku, ignore_index=None):
        for index, product in enumerate(self.inventory):
            if product.get("sku", "") == sku:
                if ignore_index is None or index != ignore_index:
                    return True
        return False

    def validate_inputs(self):
        sku = self.sku_entry.get().strip()
        name = self.name_entry.get().strip()
        quantity = self.quantity_entry.get().strip()
        min_quantity = self.min_quantity_entry.get().strip()
        price = self.price_entry.get().strip()

        if not sku or not name or not quantity or not min_quantity or not price:
            messagebox.showerror("שגיאה", "נא למלא את כל השדות")
            return None

        try:
            quantity = int(quantity)
            min_quantity = int(min_quantity)
            price = float(price)
        except ValueError:
            messagebox.showerror("שגיאה", "כמות, מינימום ומחיר חייבים להיות מספרים")
            return None

        if quantity < 0:
            messagebox.showerror("חוסר אסור", "לא ניתן להזין כמות שלילית במלאי רגיש")
            return None

        if min_quantity < 1:
            messagebox.showerror("שגיאה", "כמות מינימום חייבת להיות לפחות 1")
            return None

        if price < 0:
            messagebox.showerror("שגיאה", "מחיר לא יכול להיות שלילי")
            return None

        if quantity == 0:
            confirm = messagebox.askyesno(
                "אזהרת חוסר חמור",
                "הכמות היא 0. במלאי רגיש זה מוגדר כחוסר חמור.\nהאם להמשיך בכל זאת?"
            )
            if not confirm:
                return None

        if quantity < min_quantity:
            messagebox.showwarning(
                "התראת מלאי נמוך",
                "הכמות שהוזנה נמוכה מכמות המינימום. הפריט יסומן כהתראה."
            )

        return {
            "sku": sku,
            "name": name,
            "quantity": quantity,
            "min_quantity": min_quantity,
            "price": price
        }

    def add_product(self):
        product = self.validate_inputs()
        if product is None:
            return

        if self.sku_exists(product["sku"]):
            messagebox.showerror("שגיאה", "מק״ט זה כבר קיים במערכת")
            return

        self.inventory.append(product)
        self.save_inventory()
        self.refresh_table()
        self.clear_fields()
        messagebox.showinfo("הצלחה", "המוצר נוסף בהצלחה")

    def update_product(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showerror("שגיאה", "נא לבחור מוצר לעדכון")
            return

        index = int(selected[0])
        product = self.validate_inputs()

        if product is None:
            return

        if self.sku_exists(product["sku"], ignore_index=index):
            messagebox.showerror("שגיאה", "מק״ט זה כבר קיים למוצר אחר")
            return

        self.inventory[index] = product
        self.save_inventory()
        self.refresh_table()
        self.clear_fields()
        messagebox.showinfo("הצלחה", "המוצר עודכן בהצלחה")

    def delete_product(self):
        selected = self.table.selection()

        if not selected:
            messagebox.showerror("שגיאה", "נא לבחור מוצר למחיקה")
            return

        index = int(selected[0])
        product_name = self.inventory[index].get("name", "")

        confirm = messagebox.askyesno(
            "אישור מחיקה ממלאי רגיש",
            f"האם למחוק את המוצר: {product_name}?\nשים לב: מחיקה עלולה ליצור חוסר תיעודי."
        )

        if confirm:
            del self.inventory[index]
            self.save_inventory()
            self.refresh_table()
            self.clear_fields()
            messagebox.showinfo("הצלחה", "המוצר נמחק בהצלחה")

    def search_product(self):
        search_text = self.search_entry.get().strip().lower()

        if not search_text:
            self.refresh_table()
            return

        results = []

        for index, product in enumerate(self.inventory):
            if (
                search_text in product.get("name", "").lower()
                or search_text in product.get("sku", "").lower()
            ):
                results.append((index, product))

        self.refresh_table(results)

    def show_shortages(self):
        results = []

        for index, product in enumerate(self.inventory):
            quantity = product.get("quantity", 0)
            min_quantity = product.get("min_quantity", 1)

            if quantity < min_quantity:
                results.append((index, product))

        self.refresh_table(results)

        if not results:
            messagebox.showinfo("תקין", "לא נמצאו חוסרים או חריגות מתחת למינימום")

    def refresh_table(self, data=None):
        for row in self.table.get_children():
            self.table.delete(row)

        if data is None:
            data = list(enumerate(self.inventory))

        total_inventory_value = 0
        critical_count = 0
        warning_count = 0

        for index, product in data:
            quantity = product.get("quantity", 0)
            min_quantity = product.get("min_quantity", 1)
            price = product.get("price", 0)
            total = quantity * price
            status = self.get_status(product)

            total_inventory_value += total

            if quantity == 0:
                tag = "critical"
                critical_count += 1
            elif quantity < min_quantity:
                tag = "warning"
                warning_count += 1
            else:
                tag = "ok"

            self.table.insert(
                "",
                tk.END,
                iid=str(index),
                values=(
                    product.get("sku", ""),
                    product.get("name", ""),
                    quantity,
                    min_quantity,
                    price,
                    total,
                    status
                ),
                tags=(tag,)
            )

        total_items = len(self.inventory)

        self.status_label.config(
            text=f"סה״כ פריטים: {total_items} | חוסר חמור: {critical_count} | מתחת למינימום: {warning_count} | שווי מלאי מוצג: {total_inventory_value:.2f} ₪"
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

            self.min_quantity_entry.delete(0, tk.END)
            self.min_quantity_entry.insert(0, values[3])

            self.price_entry.delete(0, tk.END)
            self.price_entry.insert(0, values[4])

    def clear_fields(self):
        self.sku_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)
        self.min_quantity_entry.delete(0, tk.END)
        self.price_entry.delete(0, tk.END)

        selected = self.table.selection()
        if selected:
            self.table.selection_remove(selected)

    def open_catalog_file(self):
        self.update_catalog_excel()

        if os.path.exists(CATALOG_FILE):
            os.startfile(CATALOG_FILE)
        else:
            messagebox.showerror("שגיאה", "קובץ Excel לא נמצא")


if __name__ == "__main__":
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()
