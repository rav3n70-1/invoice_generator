from data_manager import DataManager

dm = DataManager()

print("\n=== Testing Delete Function ===")
print("\nBefore delete:")
inv = dm.get_inventory()
print(f"Total items: {len(inv)}")
final_items = [i for i in inv if i['name'] == 'Final']
print(f"'Final' products: {len(final_items)}")

print("\n=== Attempting to delete 'Final' Size 36 ===")
success = dm.delete_product("Final", "36")
print(f"Delete result: {success}")

print("\nAfter delete:")
inv = dm.get_inventory()
print(f"Total items: {len(inv)}")
final_items = [i for i in inv if i['name'] == 'Final']
print(f"'Final' products: {len(final_items)}")

print("\n=== Verify Size 36 is gone ===")
size_36 = [i for i in inv if i['name'] == 'Final' and str(i['size']) == '36']
print(f"'Final' Size 36 items: {len(size_36)}")
if len(size_36) == 0:
    print("✅ Delete successful!")
else:
    print("❌ Delete failed!")
