from data_manager import DataManager

dm = DataManager()

print("\n=== Testing Stock Lookup for 'Final' ===")
print("\nInventory items:")
inv = dm.get_inventory()
for i in inv:
    print(f"  Name: '{i['name']}' (type: {type(i['name'])})")
    print(f"  Size: '{i['size']}' (type: {type(i['size'])})")
    print(f"  Stock: {i['stock']}")
    print()
    break  # Just show first one

print("\n=== Test 1: Check stock for 'Final' Size 44 ===")
avail, stock = dm.check_stock_availability("Final", "44", 5)
print(f"Available: {avail}, Current Stock: {stock}")

print("\n=== Test 2: Check stock for 'Final' Size 44 (int) ===")
avail, stock = dm.check_stock_availability("Final", 44, 5)
print(f"Available: {avail}, Current Stock: {stock}")

print("\n=== Test 3: Reduce stock ===")
success, new_stock = dm.reduce_stock("Final", "44", 1)
print(f"Success: {success}, New Stock: {new_stock}")
