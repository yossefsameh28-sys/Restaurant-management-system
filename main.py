#GUI project

import tkinter as tk
from tkinter import ttk, messagebox
import oop_project as backend 

class RestaurantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Management System")
        self.root.geometry("800x600")

        # --- Initialize System Data ---
        self.tables = [backend.Table(1, 4), backend.Table(2, 2), backend.Table(3, 6)]
        self.menu = [
            backend.MenuItem(101, "Classic Burger", 150.00),
            backend.MenuItem(102, "French Fries", 40.00),
            backend.MenuItem(103, "Cola", 25.00)
        ]
        self.current_order = None 

        # --- Setup GUI ---
        self.setup_notebook()
        self.refresh_dashboard()

    def setup_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        self.tab_dashboard = ttk.Frame(self.notebook)
        self.tab_order = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_dashboard, text="Dashboard")
        self.notebook.add(self.tab_order, text="New Order")

        self.build_dashboard_tab()
        self.build_order_tab()

    def build_dashboard_tab(self):
        ttk.Label(self.tab_dashboard, text="System Dashboard", font=("Helvetica", 18, "bold")).pack(pady=20)

        self.lbl_active_tables = ttk.Label(self.tab_dashboard, text="Active Tables: 0", font=("Helvetica", 14))
        self.lbl_active_tables.pack(pady=10)

        self.lbl_total_revenue = ttk.Label(self.tab_dashboard, text="Total Revenue: 0 EGP", font=("Helvetica", 14))
        self.lbl_total_revenue.pack(pady=10)

        ttk.Button(self.tab_dashboard, text="Refresh Dashboard", command=self.refresh_dashboard).pack(pady=20)

    def build_order_tab(self):
        frame_top = ttk.LabelFrame(self.tab_order, text="1. Select Table")
        frame_top.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(frame_top, text="Table ID:").pack(side='left', padx=5)
        self.cmb_tables = ttk.Combobox(frame_top, values=[t.table_id for t in self.tables], state="readonly")
        self.cmb_tables.pack(side='left', padx=5)
        ttk.Button(frame_top, text="Start Order", command=self.start_order).pack(side='left', padx=10)

        frame_mid = ttk.LabelFrame(self.tab_order, text="2. Menu Items")
        frame_mid.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ("ID", "Name", "Price")
        self.tree_menu = ttk.Treeview(frame_mid, columns=columns, show="headings", height=5)
        self.tree_menu.heading("ID", text="Item ID")
        self.tree_menu.heading("Name", text="Name")
        self.tree_menu.heading("Price", text="Price (EGP)")
        self.tree_menu.pack(fill='both', expand=True, padx=5, pady=5)

        for item in self.menu:
            self.tree_menu.insert("", tk.END, values=(item.item_id, item.name, item.price))

        frame_action = ttk.Frame(frame_mid)
        frame_action.pack(fill='x', pady=5)
        ttk.Label(frame_action, text="Quantity:").pack(side='left', padx=5)
        self.ent_quantity = ttk.Entry(frame_action, width=10)
        self.ent_quantity.insert(0, "1")
        self.ent_quantity.pack(side='left', padx=5)
        ttk.Button(frame_action, text="Add to Order", command=self.add_to_order).pack(side='left', padx=10)

        frame_bottom = ttk.LabelFrame(self.tab_order, text="3. Checkout")
        frame_bottom.pack(fill='x', padx=10, pady=5)
        
        self.lbl_current_total = ttk.Label(frame_bottom, text="Current Total: 0.0 EGP", font=("Helvetica", 12, "bold"))
        self.lbl_current_total.pack(side='left', padx=10, pady=10)
        ttk.Button(frame_bottom, text="Checkout & Pay", command=self.checkout).pack(side='right', padx=10, pady=10)

    def start_order(self):
        try:
            selected_id = int(self.cmb_tables.get())
            table = next(t for t in self.tables if t.table_id == selected_id)
            
            table.occupy() 
            self.current_order = backend.Order(order_id=999, table=table)
            
            messagebox.showinfo("Success", f"Table {table.table_id} is now occupied. You can add items.")
            self.refresh_dashboard()
        except ValueError:
            messagebox.showwarning("Input Error", "Please select a valid table.")
        except backend.TableOccupiedError as e:
            messagebox.showerror("Business Rule Violation", str(e))

    def add_to_order(self):
        if not self.current_order:
            messagebox.showwarning("Error", "Please start an order and select a table first.")
            return

        selected = self.tree_menu.focus()
        if not selected:
            messagebox.showwarning("Error", "Please select a menu item from the list.")
            return

        item_values = self.tree_menu.item(selected, "values")
        menu_item = next(m for m in self.menu if str(m.item_id) == str(item_values[0]))
        
        try:
            qty = int(self.ent_quantity.get())
            self.current_order.add_item(menu_item, qty)
            self.lbl_current_total.config(text=f"Current Total: {self.current_order.calculate_total()} EGP")
            messagebox.showinfo("Added", f"Added {qty}x {menu_item.name} to order.")
        except ValueError:
            messagebox.showerror("Input Error", "Quantity must be a number.")
        except backend.InvalidInputError as e:
            messagebox.showerror("Validation Error", str(e))

    def checkout(self):
        if not self.current_order:
            return
            
        try:
            total = self.current_order.checkout()
            messagebox.showinfo("Checkout Success", f"Order paid! Total: {total} EGP. Table is now free.")
            
            history = backend.FileManager.load_data("sales.json")
            history.append({"order_id": self.current_order.order_id, "total": total})
            backend.FileManager.save_data("sales.json", history)

            self.current_order = None
            self.lbl_current_total.config(text="Current Total: 0.0 EGP")
            self.refresh_dashboard()
            
        except backend.EmptyOrderError as e:
            messagebox.showerror("Business Rule Violation", str(e))

    def refresh_dashboard(self):
        occupied_count = sum(1 for t in self.tables if t.is_occupied)
        self.lbl_active_tables.config(text=f"Active Tables: {occupied_count}")
        
        history = backend.FileManager.load_data("sales.json")
        total_revenue = sum(order.get("total", 0) for order in history)
        self.lbl_total_revenue.config(text=f"Total Revenue: {total_revenue} EGP")

if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantApp(root)
    root.mainloop()