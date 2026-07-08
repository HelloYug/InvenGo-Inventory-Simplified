import sys
from openpyxl import load_workbook
from datetime import datetime
from config.paths import EXCEL_TEMPLATE
from config.settings import settings
from core.inventory import InventoryManager
from core.billing import BillingSystem
from core.customer import CustomerManager
from core.accounts import AccountsManager

class InvenGo:
    def __init__(self):
        """Initialize the InvenGo application."""
        try:
            self.workbook = load_workbook(EXCEL_TEMPLATE)
            self.inventory = InventoryManager(self.workbook)
            self.customers = CustomerManager(self.workbook)
            self.accounts = AccountsManager(self.workbook)
            self.billing = BillingSystem(
                self.workbook,
                self.inventory,
                self.customers
            )
            print("System initialized successfully!")
        except Exception as e:
            print(f"Error initializing application: {e}")
            sys.exit(1)

    def run(self):
        """Main application loop."""
        while True:
            self._display_main_menu()
            choice = input("\nEnter your choice (1-9): ").strip()
            
            if choice == "1":
                self._handle_stock_view()
            elif choice == "2":
                self._handle_billing()
            elif choice == "3":
                self._handle_price_check()
            elif choice == "4":
                self._show_sales_summary()
            elif choice == "5":
                self._add_expense()
            elif choice == "6":
                self._add_new_item()
            elif choice == "7":
                self._add_stock()
            elif choice == "8":
                self._handle_bill_retrieval()
            elif choice == "9":
                self._shutdown()
                break
            else:
                print("Invalid choice. Please try again.")

    def _display_main_menu(self):
        """Display the main menu."""
        print("\n" + "=" * settings.WIDTH)
        print("🧾 INVENGO - INVENTORY SIMPLIFIED".center(settings.WIDTH))
        print("=" * settings.WIDTH)
        print("\nMain Menu:")
        print("1. Show Stock")
        print("2. Billing")
        print("3. Show Price")
        print("4. Total Sales / Accounts")
        print("5. Add Expenses")
        print("6. Add New Item")
        print("7. Add Stock")
        print("8. Show/Send Bill")
        print("9. Exit")

    def _handle_stock_view(self):
        """Handle stock viewing options."""
        print("\nStock View Options:")
        print("1. Full Stock")
        print("2. By Category")
        print("3. Specific Item")
        choice = input("Enter choice (1-3): ").strip()
        
        if choice == "1":
            self.inventory.show_stock()
        elif choice == "2":
            print("\nAvailable Categories:")
            for i, category in enumerate(self.inventory.categories.keys(), 1):
                print(f"{i}. {category}")
            cat_choice = int(input("Select category: ")) - 1
            selected_category = list(self.inventory.categories.keys())[cat_choice]
            self.inventory.show_stock(category=selected_category)
        elif choice == "3":
            code = input("Enter item code: ").upper().strip()
            self.inventory.show_stock(code=code)
        else:
            print("Invalid choice!")

    def _handle_billing(self):
        """Handle the complete billing process."""
        phone = input("\nEnter customer phone (optional): ").strip()
        
        # Format selection
        print("\nSelect Bill Format:")
        for i, fmt in enumerate(settings.BILL_FORMATS, 1):
            print(f"{i}. {fmt}")
        bill_fmt = settings.BILL_FORMATS[int(input("Choice (1-3): ")) - 1]
        
        print("\nSelect WhatsApp Format:")
        for i, fmt in enumerate(settings.WHATSAPP_FORMATS, 1):
            print(f"{i}. {fmt}")
        whatsapp_fmt = settings.WHATSAPP_FORMATS[int(input("Choice (1-3): ")) - 1]
        
        full_details = input("Include full item details? (y/n): ").lower() == 'y'
        
        self.billing.set_formats(bill_fmt, whatsapp_fmt, full_details)
        
        # Create bill
        bill_data = self.billing.make_bill(phone)
        if not bill_data:
            print("No items in bill. Returning to menu.")
            return
            
        # Display bill
        self.billing.display_bill(bill_data)
        
        # Process payment
        print("\nPayment Method:")
        print("1. Cash")
        print("2. Digital (PayTM/GPay)")
        payment_mode = int(input("Select (1-2): "))
        
        discount = 0
        if input("Apply discount? (y/n): ").lower() == 'y':
            discount = float(input("Discount amount: "))
        
        # Finalize
        bill_number = self.billing.finalize_bill(
            bill_data, 
            payment_mode, 
            discount
        )
        print(f"\nBill #{bill_number} created successfully!")
        
        # Send WhatsApp if phone provided
        if phone and input("Send via WhatsApp? (y/n): ").lower() == 'y':
            self.billing.send_whatsapp_bill(bill_data, bill_number, discount)
            print("Bill sent via WhatsApp!")

    def _handle_price_check(self):
        """Display price for a specific item."""
        print("\nPrice Check")
        code = input("Enter item code: ").upper().strip()
        if code in self.inventory.keys:
            item = self.inventory.stock[code]
            print(f"\nItem: {item[0]}")
            print(f"Size: {item[1]}GM")
            print(f"MRP: ₹{item[3]}")
            print(f"Price: ₹{item[4]}")
        else:
            print("Invalid item code!")

    def _show_sales_summary(self):
        """Display sales summary from accounts."""
        summary = self.accounts.get_sales_summary()
        print("\n" + "=" * settings.WIDTH)
        print("SALES SUMMARY".center(settings.WIDTH))
        print("=" * settings.WIDTH)
        print(f"\nCash Sales: ₹{summary['cash_sale']}")
        print(f"Digital Sales: ₹{summary['digital_sale']}")
        print(f"Total Sales: ₹{summary['cash_sale'] + summary['digital_sale']}")
        print(f"\nCash Discounts: ₹{summary['cash_discount']}")
        print(f"Digital Discounts: ₹{summary['digital_discount']}")
        print(f"Total Discounts: ₹{summary['cash_discount'] + summary['digital_discount']}")

    def _add_expense(self):
        """Add new expense to accounts."""
        print("\nAdd New Expense")
        try:
            amount = float(input("Amount: "))
            description = input("Description: ")
            self.accounts.add_expense(amount, description)
            print("Expense added successfully!")
        except ValueError:
            print("Invalid amount!")

    def _add_new_item(self):
        """Add new item to inventory."""
        print("\nAdd New Item")
        try:
            base_code = input("Base Code (e.g., ALM): ").upper().strip()
            category = input("Category: ").title().strip()
            item_code = input("Item Code: ").upper().strip()
            name = input("Item Name: ").title().strip()
            size = int(input("Size (in GM): "))
            mrp = float(input("MRP: "))
            price = float(input("Selling Price: "))
            stock = int(input("Initial Stock: "))
            
            # Find first empty row
            row = 2
            while self.inventory.sheet[f"A{row}"].value is not None:
                row += 1
                
            # Add new item
            self.inventory.sheet[f"A{row}"] = base_code
            self.inventory.sheet[f"B{row}"] = category
            self.inventory.sheet[f"C{row}"] = item_code
            self.inventory.sheet[f"D{row}"] = name
            self.inventory.sheet[f"E{row}"] = size
            self.inventory.sheet[f"F{row}"] = "GM"
            self.inventory.sheet[f"G{row}"] = mrp
            self.inventory.sheet[f"H{row}"] = price
            self.inventory.sheet[f"I{row}"] = f"={stock}"
            self.inventory.sheet[f"J{row}"] = "=0"
            self.inventory.sheet[f"K{row}"] = f"=I{row}-J{row}"
            
            self.workbook.save(EXCEL_TEMPLATE)
            print("Item added successfully!")
            self.inventory = InventoryManager(self.workbook)  # Refresh inventory
        except ValueError:
            print("Invalid input! Please enter correct values.")

    def _add_stock(self):
        """Add stock to existing item."""
        print("\nAdd Stock")
        code = input("Enter item code: ").upper().strip()
        if code not in self.inventory.keys:
            print("Invalid item code!")
            return
            
        try:
            quantity = int(input("Quantity to add: "))
            if quantity <= 0:
                print("Quantity must be positive!")
                return
                
            if self.inventory.add_stock(code, quantity):
                print("Stock updated successfully!")
                self.workbook.save(EXCEL_TEMPLATE)
                self.inventory = InventoryManager(self.workbook)  # Refresh inventory
        except ValueError:
            print("Invalid quantity!")

    def _handle_bill_retrieval(self):
        """Handle bill retrieval and resending."""
        print("\nBill Options:")
        print("1. Search by Phone")
        print("2. Search by Bill Number")
        choice = input("Select (1-2): ").strip()
        
        if choice == "1":
            phone = input("Enter phone number: ").strip()
            customer = self.customers.get_customer(phone)
            if not customer:
                print("No bills found for this number!")
                return
                
            print(f"\nFound {len(customer['bills']} bill(s) for this number:")
            for i, bill_num in enumerate(customer['bills'], 1):
                print(f"{i}. {bill_num}")
                
            if input("View a bill? (y/n): ").lower() == 'y':
                bill_choice = int(input("Enter bill number (1-{}): ".format(len(customer['bills'])))) - 1
                self._display_bill(customer['bills'][bill_choice])
                
        elif choice == "2":
            bill_num = input("Enter bill number (format {}XXXX): ".format(settings.BILL_CODE)).upper().strip()
            self._display_bill(bill_num)
        else:
            print("Invalid choice!")

    def _display_bill(self, bill_number):
        """Display a saved bill."""
        # Implementation would search the Bills sheet and display
        print(f"\nDisplaying bill {bill_number}...")
        # Actual implementation would parse the Excel sheet
        
    def _shutdown(self):
        """Cleanup before exiting."""
        self.workbook.save(EXCEL_TEMPLATE)
        print("\nData saved successfully. Goodbye!")

if __name__ == "__main__":
    app = InvenGo()
    app.run()