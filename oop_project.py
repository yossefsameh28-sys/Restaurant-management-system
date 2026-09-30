# oop project

import json
import os
from abc import ABC, abstractmethod
from typing import List

# ==========================================
# CUSTOM EXCEPTIONS
# ==========================================
class RestaurantError(Exception):
    """base exception for all restaurant,related errors"""
    pass

class TableOccupiedError(RestaurantError):
    """raised when trying to assign an already occupied table"""
    pass

class InvalidInputError(RestaurantError):
    """raised when validation fails for names, prices or quantities"""
    pass

class EmptyOrderError(RestaurantError):
    """raised when trying to checkout an order with no items"""
    pass


# ==========================================
# FILE HANDLING
# ==========================================

class FileManager:
    @staticmethod
    def save_data(filename: str, data: list):
        """Saves a list of dictionaries to a JSON file with error handling"""
        try:
            with open(filename, 'w') as file:
                json.dump(data, file)
        except IOError as e:
            print(f"Error saving to {filename}: {e}")

    @staticmethod
    def load_data(filename: str) -> list:
        """Loads data from a JSON file safely"""
        if not os.path.exists(filename):
            return []
        
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except json.JSONDecodeError:
            print(f"Warning: {filename} contains invalid or corrupted JSON,Returning empty data")
            return []
        except IOError as e:
            print(f"Error reading {filename}: {e}")
            return []


# ==========================================
# CORE MODELS & BUSINESS LOGIC
# ==========================================

class Person(ABC):
    def __init__(self, name: str, phone: str):
        if not name or not name.strip():
            raise InvalidInputError("Name cannot be empty or whitespace")
        if not phone.isdigit() or len(phone) <= 8:
            raise InvalidInputError("Phone number must be at least 8 digits and contain no letters")
            
        self.name = name.strip()
        self.phone = phone.strip()
        
    @abstractmethod
    def get_details(self) -> str:
        pass


class Customer(Person):
    def __init__(self, name: str, phone: str, customer_id: str):
        super().__init__(name, phone)
        if not customer_id:
            raise InvalidInputError("Customer ID cannot be empty")
        self.customer_id = customer_id
        
    def get_details(self) -> str:
        return f"Customer [{self.customer_id}]: {self.name} - {self.phone}"


class Table:
    def __init__(self, table_id: int, capacity: int):
        if not isinstance(table_id, int) or table_id <= 0:
            raise InvalidInputError("Table ID must be a positive integer.")
        if not isinstance(capacity, int) or capacity <= 0:
            raise InvalidInputError("Table capacity must be at least 1.")
            
        self.table_id = table_id
        self.capacity = capacity
        self._is_occupied = False 

    @property
    def is_occupied(self) -> bool:
        return self._is_occupied

    def occupy(self):
        if self._is_occupied:
            raise TableOccupiedError(f"Table {self.table_id} is already occupied! Cannot assign.")
        self._is_occupied = True

    def free(self):
        self._is_occupied = False


class MenuItem:
    def __init__(self, item_id: int, name: str, price: float):
        if not name.strip():
            raise InvalidInputError("Menu item name cannot be empty.")
        if price <= 0:
            raise InvalidInputError("Menu item price must be greater than zero.")
            
        self.item_id = item_id
        self.name = name.strip()
        self.price = float(price)


class OrderItem:
    def __init__(self, menu_item: MenuItem, quantity: int):
        if not isinstance(menu_item, MenuItem):
            raise TypeError("Expected a MenuItem object.")
        if not isinstance(quantity, int) or quantity <= 0:
            raise InvalidInputError("Quantity must be a positive whole number.")
            
        self.menu_item = menu_item
        self.quantity = quantity

    def get_subtotal(self) -> float:
        return self.menu_item.price * self.quantity


class Order:
    def __init__(self, order_id: int, table: Table):
        if not isinstance(table, Table):
            raise TypeError("Order must be assigned to a valid Table object.")
            
        self.order_id = order_id
        self.table = table
        self.items: List[OrderItem] = []
        self.is_paid = False

    def add_item(self, menu_item: MenuItem, quantity: int):
        try:
            item = OrderItem(menu_item, quantity)
            self.items.append(item)
        except (InvalidInputError, TypeError) as e:
            print(f"Failed to add item to order: {e}")

    def calculate_total(self) -> float:
        total = sum(item.get_subtotal() for item in self.items)
        return round(total, 2)

    def checkout(self) -> float:
        if self.is_paid:
            raise RestaurantError("This order has already been paid.")
        if len(self.items) == 0:
            raise EmptyOrderError("Cannot checkout an empty order. Please add items first.")
            
        self.is_paid = True
        self.table.free()
        return self.calculate_total()

# ==========================================
# SYSTEM SIMULATION (TESTING THE CODE)
# ==========================================
if __name__ == "__main__":
    print("--- 1. Setting up the Restaurant ---")
    table1 = Table(table_id=1, capacity=4)
    table2 = Table(table_id=2, capacity=2)
    
    burger = MenuItem(item_id=101, name="Classic Burger", price=150.00)
    fries = MenuItem(item_id=102, name="French Fries", price=40.00)
    cola = MenuItem(item_id=103, name="Cola", price=25.00)
    
    customer = Customer(name="Youssef Sameh Zaky", phone="01012345678", customer_id="C-001")
    print(customer.get_details())

    print("\n--- 2. Seating the Customer & Ordering ---")
    try:
        table1.occupy()
        print(f"Table {table1.table_id} is now occupied")
        table1.occupy() # Triggers TableOccupiedError
    except TableOccupiedError as e:
        print(f"EXPECTED ERROR CAUGHT: {e}")

    my_order = Order(order_id=5001, table=table1)
    my_order.add_item(menu_item=burger, quantity=2)
    my_order.add_item(menu_item=fries, quantity=1)
    my_order.add_item(menu_item=cola, quantity=2)
    print(f"Current Order Total: {my_order.calculate_total()} EGP")

    print("\n--- 3. Testing Empty Order Rule ---")
    empty_order = Order(order_id=5002, table=table2)
    try:
        empty_order.checkout()
    except EmptyOrderError as e:
        print(f"EXPECTED ERROR CAUGHT: {e}")

    print("\n--- 4. Checking Out & Saving Data ---")
    final_total = my_order.checkout()
    print(f"Checkout successful! Final amount to pay: {final_total} EGP")
    print(f"Is Table {table1.table_id} free now? {not table1.is_occupied}")

    order_data_to_save = [
        {
            "order_id": my_order.order_id,
            "customer_name": customer.name,
            "total_paid": final_total,
            "items": [{"name": item.menu_item.name, "qty": item.quantity} for item in my_order.items]
        }
    ]

    FileManager.save_data("restaurant_history.json", order_data_to_save)
    print("\nOrder saved to 'restaurant_history.json'.")
    
    loaded_data = FileManager.load_data("restaurant_history.json")
    print(f"Data loaded from file:\n{json.dumps(loaded_data, indent=2)}")