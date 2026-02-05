"""
Quick test of data manager inventory functions
"""
from data_manager import DataManager

dm = DataManager()

print("=== Testing Inventory Functions ===\n")

# Test 1: Check stock availability
print("TEST 1: Check stock availability")
available, stock = dm.check_stock_availability("test1", "36", 1)
print(f"  test1 Size 36 - Available: {available}, Current Stock: {stock}")

# Test 2: Reduce stock
print("\nTEST 2: Reduce stock")
print(f"  Before: Stock = {stock}")
success, new_stock = dm.reduce_stock("test1", "36", 1)
print(f"  After reducing 1: Success = {success}, New Stock = {new_stock}")

# Test 3: Verify reduction worked
print("\nTEST 3: Verify reduction")
available, stock = dm.check_stock_availability("test1", "36", 1)
print(f"  test1 Size 36 - Available: {available}, Current Stock: {stock}")

# Test 4: Delete product
print("\nTEST 4: Delete product")
success = dm.delete_product("test2", "36")
print(f"  Deleted test2 Size 36: {success}")

# Test 5: View all inventory
print("\nTEST 5: Current Inventory")
inventory = dm.get_inventory()
print(f"  Total items: {len(inventory)}")
for item in inventory[:5]:  # Show first 5
    print(f"    {item['name']} Size {item['size']}: {item['stock']} units")
