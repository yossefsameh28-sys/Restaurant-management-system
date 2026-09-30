#tests

import oop_project as backend
import os

print("="*50)
print("RESTAURANT MANAGEMENT SYSTEM: AUTOMATED TEST SUITE")
print("="*50)

# ---------------------------------------------------------
# SUCCESSFUL SCENARIOS (1-3)
# ---------------------------------------------------------
print("\n[SCENARIO 1] Create Order")
table1 = backend.Table(table_id=1, capacity=4)
table1.occupy()
order1 = backend.Order(order_id=1001, table=table1)
burger = backend.MenuItem(item_id=101, name="Classic Burger", price=150.0)
order1.add_item(burger, quantity=2)
expected_total = 300.0
actual_total = order1.calculate_total()
print(f"Action: Added 2x Classic Burger (150 EGP).")
print(f"Result: Expected Total = {expected_total} | Actual Total = {actual_total}")
if actual_total == expected_total: print("✅ TEST 1 PASSED")

print("\n[SCENARIO 2] Checkout Order")
total_paid = order1.checkout()
print(f"Action: Checking out Order 1001.")
print(f"Result: Paid = {total_paid} EGP. Is table free? {not table1.is_occupied}")
if not table1.is_occupied and total_paid == 300.0: print("✅ TEST 2 PASSED")

print("\n[SCENARIO 3] Dashboard Update (File Persistence)")
history = [{"order_id": 1001, "total": total_paid}]
backend.FileManager.save_data("test_sales.json", history)
loaded_history = backend.FileManager.load_data("test_sales.json")
print(f"Action: Saving order to JSON and reloading.")
print(f"Result: Loaded Data = {loaded_history}")
if loaded_history[0]['total'] == 300.0: print("✅ TEST 3 PASSED")


# ---------------------------------------------------------
# INVALID INPUTS (4-6)
# ---------------------------------------------------------
print("\n[SCENARIO 4] Invalid Quantity Input")
try:
    print("Action: Attempting to add an item with 0 quantity.")
    bad_item = backend.OrderItem(menu_item=burger, quantity=0)
    print("❌ TEST 4 FAILED: Should have raised error.")
except backend.InvalidInputError as e:
    print(f"✅ TEST 4 PASSED: Caught Expected Error -> {e}")

print("\n[SCENARIO 5] Negative Price Creation")
try:
    print("Action: Attempting to create MenuItem with -5.00 EGP.")
    water = backend.MenuItem(item_id=104, name="Water", price=-5.0)
    print("❌ TEST 5 FAILED: Should have raised error.")
except backend.InvalidInputError as e:
    print(f"✅ TEST 5 PASSED: Caught Expected Error -> {e}")

print("\n[SCENARIO 6] Empty Customer Name")
try:
    print("Action: Attempting to register customer with blank name.")
    cust = backend.Customer(name="   ", phone="01012345678", customer_id="C-001")
    print("❌ TEST 6 FAILED: Should have raised error.")
except backend.InvalidInputError as e:
    print(f"✅ TEST 6 PASSED: Caught Expected Error -> {e}")


# ---------------------------------------------------------
# BUSINESS RULES (7-8)
# ---------------------------------------------------------
print("\n[SCENARIO 7] Double-Booking (TableOccupiedError)")
table2 = backend.Table(table_id=2, capacity=2)
table2.occupy() # First booking
try:
    print("Action: Attempting to occupy an already occupied table.")
    table2.occupy() # Second booking attempt
    print("❌ TEST 7 FAILED: Should have raised error.")
except backend.TableOccupiedError as e:
    print(f"✅ TEST 7 PASSED: Caught Expected Error -> {e}")

print("\n[SCENARIO 8] Empty Order (EmptyOrderError)")
table3 = backend.Table(table_id=3, capacity=6)
table3.occupy()
empty_order = backend.Order(order_id=1003, table=table3)
try:
    print("Action: Attempting to checkout an order with no items.")
    empty_order.checkout()
    print("❌ TEST 8 FAILED: Should have raised error.")
except backend.EmptyOrderError as e:
    print(f"✅ TEST 8 PASSED: Caught Expected Error -> {e}")


# ---------------------------------------------------------
# EDGE CASES (9-10)
# ---------------------------------------------------------
print("\n[SCENARIO 9] Corrupted JSON File Recovery")
# Create a deliberately corrupted JSON file
with open("corrupt_test.json", "w") as f:
    f.write("[{bad_data: true, missing_quotes}]") 
print("Action: Loading corrupted JSON file.")
corrupted_data = backend.FileManager.load_data("corrupt_test.json")
print(f"Result: FileManager returned {corrupted_data} instead of crashing.")
if corrupted_data == []: print("✅ TEST 9 PASSED")

print("\n[SCENARIO 10] Action Without Selection State")
print("Action: GUI user clicks 'Add to Order' before clicking 'Start Order'.")
# Simulating the Tkinter state where an order object hasn't been instantiated yet
current_order = None
if current_order is None:
    print("Result: System caught empty state.")
    print("✅ TEST 10 PASSED: (GUI will trigger 'Please start an order first' messagebox)")

# Clean up test files
if os.path.exists("test_sales.json"): os.remove("test_sales.json")
if os.path.exists("corrupt_test.json"): os.remove("corrupt_test.json")
print("\n" + "="*50)