﻿import csv
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from fuzzywuzzy import process


class StockManager:
    FILENAME = "stock.csv"

    def __init__(self, main_menu_callback):
        """Initialize the StockManager class."""
        self.main_menu_callback = main_menu_callback
        self.root = tk.Tk()
        self.root.title("Stock Control - Add Stock")

        # Set window size and center it
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.center_window()

        # Read existing stock data
        self.stock_items = self.read_stock()
        sizes = ["XS", "S", "M", "L", "XL"]

        # Entry for item name
        tk.Label(self.root, text="Item Name", font=("Arial", 12)).grid(row=0, column=0, padx=20, pady=10, sticky='e')
        self.name_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.name_var, font=("Arial", 12)).grid(row=0, column=1, padx=20, pady=10)

        # Dropdown to select size
        tk.Label(self.root, text="Select Size", font=("Arial", 12)).grid(row=1, column=0, padx=20, pady=10, sticky='e')
        self.size_dropdown = ttk.Combobox(self.root, values=sizes, font=("Arial", 12))
        self.size_dropdown.grid(row=1, column=1, padx=20, pady=10)

        # Entry for price
        tk.Label(self.root, text="Price", font=("Arial", 12)).grid(row=2, column=0, padx=20, pady=10, sticky='e')
        self.price_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.price_var, font=("Arial", 12)).grid(row=2, column=1, padx=20, pady=10)

        # Entry for quantity
        tk.Label(self.root, text="Quantity", font=("Arial", 12)).grid(row=3, column=0, padx=20, pady=10, sticky='e')
        self.quantity_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.quantity_var, font=("Arial", 12)).grid(row=3, column=1, padx=20, pady=10)

        # Button to add stock
        tk.Button(self.root, text="Add Stock", command=self.add_stock, font=("Arial", 12)).grid(row=4, column=0,
                                                                                                columnspan=2, pady=20)

        # Button to return to main menu
        tk.Button(self.root, text="Back to Main Menu", command=self.go_back, font=("Arial", 12)).grid(row=5, column=0,
                                                                                                      columnspan=2,
                                                                                                      pady=10)

    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def read_stock(self):
        """Read stock from the CSV file."""
        stock_list = []
        try:
            with open(self.FILENAME, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if row:  # Ensure the row is not empty
                        stock_list.append(row)
        except FileNotFoundError:
            messagebox.showerror("Error", "Stock file not found.")
        return stock_list

    def validate_inputs(self):
        """Validate the input fields."""
        name = self.name_var.get().strip()
        size = self.size_dropdown.get()
        price = self.price_var.get().strip()
        quantity = self.quantity_var.get().strip()

        if not name:
            return False, "Item name cannot be empty."
        if not size:
            return False, "Size must be selected."
        if not price or not price.replace('.', '', 1).isdigit() or float(price) <= 0:
            return False, "Price must be a positive number."
        if not quantity.isdigit() or int(quantity) <= 0:
            return False, "Quantity must be a positive integer."

        return True, ""

    def item_exists(self, name, size):
        """Check if an item with the same name and size already exists."""
        return any(item[0] == name and item[3] == size for item in self.stock_items)

    def find_similar_item(self, name):
        """Find similar item names using fuzzy matching."""
        names = [item[0] for item in self.stock_items]
        return process.extractOne(name, names, score_cutoff=85)

    def prompt_user(self, suggested_name):
        """Prompt the user to confirm if the suggested item is what they meant."""
        response = messagebox.askyesno(
            "Similar Item Found",
            f"An item with a similar name '{suggested_name}' already exists. Did you mean to update this item?"
        )
        return response

    def add_stock(self):
        """Add a new stock item."""
        is_valid, message = self.validate_inputs()
        if not is_valid:
            messagebox.showerror("Error", message)
            return

        name = self.name_var.get().strip()
        size = self.size_dropdown.get()
        price = float(self.price_var.get().strip())
        quantity = int(self.quantity_var.get().strip())

        similar_item = self.find_similar_item(name)
        if similar_item:
            suggested_name = similar_item[0]
            if self.prompt_user(suggested_name):
                # If user confirms, check if the item with the suggested name and size exists
                if self.item_exists(suggested_name, size):
                    messagebox.showerror("Error",
                                         f"An item with name '{suggested_name}' and size '{size}' already exists.")
                    return
                else:
                    # Treat as new item
                    name = suggested_name
            else:
                # Proceed with adding the item normally
                pass

        # Add new stock item
        new_item = [name, str(quantity), str(price), size, "1" if quantity > 0 else "0"]
        self.stock_items.append(new_item)

        # Write updated stock data back to CSV
        try:
            with open(self.FILENAME, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['name', 'quantity', 'price', 'size', 'available'])  # Write header
                writer.writerows(self.stock_items)
            messagebox.showinfo("Success", f"Added new stock item: {name} ({size}).")
        except IOError:
            messagebox.showerror("Error", "Failed to update the stock file.")

    def go_back(self):
        """Close the current window and return to the main menu."""
        self.root.destroy()
        self.main_menu_callback()

    def run(self):
        """Run the StockManager."""


class StockAvailabilityUpdater:
    FILENAME = "stock.csv"

    def __init__(self, main_menu_callback):
        """Initialize the StockAvailabilityUpdater class."""
        self.main_menu_callback = main_menu_callback
        self.root = tk.Tk()
        self.root.title("Stock Control - Update Quantity")

        # Set window size and center it
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        self.center_window()

        # Read existing stock data
        self.stock_items = self.read_stock()
        item_names = list(set(item[0] for item in self.stock_items))  # Unique item names

        # Dropdown to select stock item
        tk.Label(self.root, text="Select Item", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.item_dropdown = ttk.Combobox(self.root, values=item_names, font=("Arial", 12))
        self.item_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.item_dropdown.bind("<<ComboboxSelected>>", self.update_size_dropdown)

        # Dropdown to select size
        tk.Label(self.root, text="Select Size", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.size_dropdown = ttk.Combobox(self.root, values=[], font=("Arial", 12))
        self.size_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Dropdown to select operation
        tk.Label(self.root, text="Operation", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.operation_var = tk.StringVar(value="Add Copies")
        self.operation_dropdown = ttk.Combobox(self.root, textvariable=self.operation_var,
                                               values=["Add Copies", "Sell Copies"], font=("Arial", 12))
        self.operation_dropdown.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        # Entry to set quantity
        tk.Label(self.root, text="Quantity", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.quantity_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.quantity_var, font=("Arial", 12)).grid(row=3, column=1, padx=10, pady=10,
                                                                                     sticky="w")

        # Button to update quantity
        tk.Button(self.root, text="Update Quantity", command=self.update_quantity, font=("Arial", 12), width=20).grid(
            row=4, column=0, columnspan=2, pady=20)

        # Button to return to main menu
        tk.Button(self.root, text="Back to Main Menu", command=self.go_back, font=("Arial", 12), width=20).grid(row=5,
                                                                                                                column=0,
                                                                                                                columnspan=2,
                                                                                                                pady=10)

    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def read_stock(self):
        """Read stock from the CSV file."""
        stock_list = []
        try:
            with open(self.FILENAME, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if row:  # Ensure the row is not empty
                        stock_list.append(row)
        except FileNotFoundError:
            messagebox.showerror("Error", "Stock file not found.")
        return stock_list

    def update_size_dropdown(self, event):
        """Update the size dropdown based on the selected item."""
        selected_item = self.item_dropdown.get()
        sizes = [item[3] for item in self.stock_items if item[0] == selected_item]
        self.size_dropdown.config(values=sizes)
        self.size_dropdown.set("")  # Clear the selection

    def validate_inputs(self):
        """Validate the input fields."""
        item_name = self.item_dropdown.get()
        size = self.size_dropdown.get()
        quantity = self.quantity_var.get().strip()
        operation = self.operation_var.get()

        if not item_name:
            return False, "No item selected."
        if not size:
            return False, "No size selected."
        if not quantity.isdigit() or int(quantity) <= 0:
            return False, "Quantity must be a positive integer."
        if operation not in ["Add Copies", "Sell Copies"]:
            return False, "Invalid operation selected."

        return True, ""

    def update_quantity(self):
        """Update the quantity of the selected stock item."""
        is_valid, message = self.validate_inputs()
        if not is_valid:
            messagebox.showerror("Error", message)
            return

        item_name = self.item_dropdown.get()
        size = self.size_dropdown.get()
        quantity = int(self.quantity_var.get().strip())
        operation = self.operation_var.get()

        # Read current stock data
        stock = self.read_stock()

        # Update quantity based on operation
        updated = False
        for row in stock:
            if row[0] == item_name and row[3] == size:
                current_quantity = int(row[1])
                if operation == "Add Copies":
                    new_quantity = current_quantity + quantity
                    row[1] = str(new_quantity)
                    # Set availability to 1 if quantity is greater than 0
                    if new_quantity > 0:
                        row[4] = "1"
                elif operation == "Sell Copies":
                    if quantity > current_quantity:
                        messagebox.showerror("Error", "Not enough copies available for this transaction.")
                        return
                    new_quantity = current_quantity - quantity
                    row[1] = str(new_quantity)
                    # Set availability to 0 if quantity reaches 0
                    if new_quantity <= 0:
                        row[1] = "0"
                        row[4] = "0"
                updated = True
                break  # Exit loop after updating

        if updated:
            # Write updated stock data back to CSV
            try:
                with open(self.FILENAME, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['name', 'quantity', 'price', 'size', 'available'])  # Write header
                    writer.writerows(stock)
                messagebox.showinfo("Success", f"Updated quantity for {item_name} ({size}).")
            except IOError:
                messagebox.showerror("Error", "Failed to update the stock file.")
        else:
            messagebox.showwarning("Warning", "Selected item and size not found or no updates made.")

    def go_back(self):
        """Close the current window and return to the main menu."""
        self.root.destroy()
        self.main_menu_callback()

    def run(self):
        """Run the StockAvailabilityUpdater."""
        self.root.mainloop()


class StockPriceUpdater:
    FILENAME = "stock.csv"

    def __init__(self, main_menu_callback):
        """Initialize the StockPriceUpdater class."""
        self.main_menu_callback = main_menu_callback
        self.root = tk.Tk()
        self.root.title("Stock Control - Update Price")

        # Set window size and center it
        self.root.geometry("400x250")
        self.root.resizable(False, False)
        self.center_window()

        # Read existing stock data
        self.stock_items = self.read_stock()
        item_names = list(set(item[0] for item in self.stock_items))  # Unique item names

        # Dropdown to select stock item
        tk.Label(self.root, text="Select Item", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.item_dropdown = ttk.Combobox(self.root, values=item_names, font=("Arial", 12))
        self.item_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.item_dropdown.bind("<<ComboboxSelected>>", self.update_size_dropdown)

        # Dropdown to select size
        tk.Label(self.root, text="Select Size", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.size_dropdown = ttk.Combobox(self.root, values=[], font=("Arial", 12))
        self.size_dropdown.grid(row=1, column=1, padx=10, pady=10, sticky="w")

        # Entry to set new price
        tk.Label(self.root, text="New Price", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.price_var = tk.StringVar()
        tk.Entry(self.root, textvariable=self.price_var, font=("Arial", 12)).grid(row=2, column=1, padx=10, pady=10,
                                                                                  sticky="w")

        # Button to update price
        tk.Button(self.root, text="Update Price", command=self.update_price, font=("Arial", 12), width=20).grid(row=3,
                                                                                                                column=0,
                                                                                                                columnspan=2,
                                                                                                                pady=20)

        # Button to return to main menu
        tk.Button(self.root, text="Back to Main Menu", command=self.go_back, font=("Arial", 12), width=20).grid(row=4,
                                                                                                                column=0,
                                                                                                                columnspan=2,
                                                                                                                pady=10)

    def center_window(self):
        """Center the window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def read_stock(self):
        """Read stock from the CSV file."""
        stock_list = []
        try:
            with open(self.FILENAME, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if row:  # Ensure the row is not empty
                        stock_list.append(row)
        except FileNotFoundError:
            messagebox.showerror("Error", "Stock file not found.")
        return stock_list

    def update_size_dropdown(self, event):
        """Update the size dropdown based on the selected item."""
        selected_item = self.item_dropdown.get()
        sizes = [item[3] for item in self.stock_items if item[0] == selected_item]
        self.size_dropdown.config(values=sizes)
        self.size_dropdown.set("")  # Clear the selection

    def validate_inputs(self):
        """Validate the input fields."""
        item_name = self.item_dropdown.get()
        size = self.size_dropdown.get()
        price = self.price_var.get().strip()

        if not item_name:
            return False, "No item selected."
        if not size:
            return False, "No size selected."
        if not price or not price.replace('.', '', 1).isdigit() or float(price) <= 0:
            return False, "Price must be a positive number."

        return True, ""

    def update_price(self):
        """Update the price of the selected stock item."""
        is_valid, message = self.validate_inputs()
        if not is_valid:
            messagebox.showerror("Error", message)
            return

        item_name = self.item_dropdown.get()
        size = self.size_dropdown.get()
        new_price = float(self.price_var.get().strip())

        # Read current stock data
        stock = self.read_stock()

        # Update price for the selected item and size
        updated = False
        for row in stock:
            if row[0] == item_name and row[3] == size:
                row[2] = str(new_price)
                updated = True
                break  # Exit loop after updating

        if updated:
            # Write updated stock data back to CSV
            try:
                with open(self.FILENAME, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['name', 'quantity', 'price', 'size', 'available'])  # Write header
                    writer.writerows(stock)
                messagebox.showinfo("Success", f"Updated price for {item_name} ({size}).")
            except IOError:
                messagebox.showerror("Error", "Failed to update the stock file.")
        else:
            messagebox.showwarning("Warning", "Selected item and size not found or no updates made.")

    def go_back(self):
        """Close the current window and return to the main menu."""
        self.root.destroy()
        self.main_menu_callback()

    def run(self):
        """Run the StockPriceUpdater."""
        self.root.mainloop()


class StockViewer:
    FILENAME = "stock.csv"

    def __init__(self, main_menu_callback):
        """Initialize the StockViewer class."""
        self.main_menu_callback = main_menu_callback
        self.root = tk.Tk()
        self.root.title("Stock Control - View Available Items")

        # Frame for the main content
        content_frame = tk.Frame(self.root, padx=10, pady=10)
        content_frame.pack(expand=True, fill=tk.BOTH)

        # Header Label
        tk.Label(content_frame, text="Available Items", font=("Helvetica", 16, "bold")).pack(pady=5)

        # ScrolledText for displaying items
        self.text_area = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD, width=80, height=20,
                                                   font=("Helvetica", 12))
        self.text_area.pack(expand=True, fill=tk.BOTH)

        # Load and display stock data
        self.display_stock()

        # Back to Main Menu Button
        tk.Button(content_frame, text="Back to Main Menu", command=self.go_back, font=("Helvetica", 12)).pack(pady=10)

    def read_stock(self):
        """Read stock from the CSV file."""
        stock_list = []
        try:
            with open(self.FILENAME, mode='r') as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    if row:  # Ensure the row is not empty
                        stock_list.append(row)
        except FileNotFoundError:
            messagebox.showerror("Error", "Stock file not found.")
        return stock_list

    def display_stock(self):
        """Display available stock items in the text area."""
        available_items = [item for item in self.read_stock() if item[4] == "1"]  # Filter items with availability = 1

        if not available_items:
            self.text_area.insert(tk.END, "No available items in stock.\n")
            return

        for item in available_items:
            display_text = f"Name: {item[0]}\nQuantity: {item[1]}\nPrice: ${item[2]}\nSize: {item[3]}\n"
            display_text += "-" * 40 + "\n"
            self.text_area.insert(tk.END, display_text)

    def go_back(self):
        """Close the current window and return to the main menu."""
        self.root.destroy()
        self.main_menu_callback()

    def run(self):
        """Run the StockViewer."""
        self.root.mainloop()


def main_menu():
    """Main program to choose between adding stock, updating stock, and viewing available items."""

    def open_add_stock():
        main_menu_window.destroy()
        manager = StockManager(main_menu)
        manager.run()

    def open_update_availability():
        main_menu_window.destroy()
        updater = StockAvailabilityUpdater(main_menu)
        updater.run()

    def open_update_price():
        main_menu_window.destroy()
        updater = StockPriceUpdater(main_menu)
        updater.run()

    def open_view_stock():
        main_menu_window.destroy()
        viewer = StockViewer(main_menu)
        viewer.run()

    # Create the main menu window
    global main_menu_window
    main_menu_window = tk.Tk()
    main_menu_window.title("Stock Control - Main Menu")

    # Set window size and center it
    main_menu_window.geometry("400x300")
    main_menu_window.resizable(False, False)
    center_window(main_menu_window)

    # Create and style the label
    tk.Label(main_menu_window, text="Choose an action:", font=("Arial", 14)).pack(pady=20)

    # Create and style buttons
    button_options = [
        ("Add Stock", open_add_stock),
        ("Update Availability", open_update_availability),
        ("Update Price", open_update_price),
        ("View Available Items", open_view_stock)
    ]

    for text, command in button_options:
        tk.Button(main_menu_window, text=text, command=command, font=("Arial", 12), width=25).pack(pady=10)

    main_menu_window.mainloop()


def center_window(window):
    """Center the window on the screen."""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')


if __name__ == "__main__":
    main_menu()
