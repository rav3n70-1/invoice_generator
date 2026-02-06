import unittest
import os
from data_manager import DataManager
from datetime import datetime

class TestExpenses(unittest.TestCase):
    def setUp(self):
        self.dm = DataManager()
        # Use a temporary file for testing (or just ensure we clean up)
        # For simplicity, we'll just clean up the specific test entry
        self.test_expense = {
            'date': '01/01/2025',
            'category': 'Test Category',
            'amount': 999.99,
            'description': 'Test Description',
            'related_product': 'Test Product'
        }

    def test_add_and_get_expense(self):
        # Add
        self.dm.add_expense(self.test_expense)
        
        # Get
        expenses = self.dm.get_expenses()
        self.assertTrue(len(expenses) > 0)
        
        found = False
        for ex in expenses:
            if ex['description'] == 'Test Description' and float(ex['amount']) == 999.99:
                found = True
                break
        self.assertTrue(found)

    def test_delete_expense(self):
        # Ensure it exists
        self.dm.add_expense(self.test_expense)
        
        # Delete
        success = self.dm.delete_expense(self.test_expense)
        self.assertTrue(success)
        
        # Verify deleted
        expenses = self.dm.get_expenses()
        found = False
        for ex in expenses:
            if ex['description'] == 'Test Description' and float(ex['amount']) == 999.99:
                found = True
                break
        self.assertFalse(found)

    def test_categories(self):
        cat = "New Test Cat"
        self.dm.add_expense_category(cat)
        cats = self.dm.get_expense_categories()
        self.assertIn(cat, cats)
        
        self.dm.delete_expense_category(cat)
        cats = self.dm.get_expense_categories()
        self.assertNotIn(cat, cats)

if __name__ == '__main__':
    unittest.main()
