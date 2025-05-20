import pyperclip
from datetime import datetime
from time import sleep
from tabulate import tabulate
from openpyxl.comments import Comment
from config.settings import settings
from core.utils import (
    format_number,
    image_to_clipboard,
    open_whatsapp,
    close_browser_tab
)
from pyautogui import hotkey, press

class BillingSystem:
    def __init__(self, workbook, inventory, customer_manager):
        """
        Initialize billing system with dependencies.
        
        Args:
            workbook: OpenPyXL Workbook object
            inventory: InventoryManager instance
            customer_manager: CustomerManager instance
        """
        self.workbook = workbook
        self.inventory = inventory
        self.customers = customer_manager
        self.bills_sheet = workbook["Bills"]
        self.sales_sheet = workbook["Sales & Stocks"]
        self.accounts_sheet = workbook["Accounts"]
        
        # Default formats
        self.bill_format = settings.BILL_FORMATS[0]
        self.whatsapp_format = settings.WHATSAPP_FORMATS[0]
        self.include_full_details = False

    def set_formats(self, bill_fmt, whatsapp_fmt, full_details=False):
        """
        Set display formats for bills.
        
        Args:
            bill_fmt: Bill display format (Compact/Detailed/Full)
            whatsapp_fmt: WhatsApp message format (Simple/Detailed/Professional)
            full_details: Whether to include full item details in bill
        """
        self.bill_format = bill_fmt
        self.whatsapp_format = whatsapp_fmt
        self.include_full_details = full_details

    def make_bill(self, phone=""):
        """
        Create a new bill interactively.
        
        Args:
            phone: Customer phone number (optional)
            
        Returns:
            dict: Bill data including items, total, and packaging details
        """
        bill_items = []
        total_weight = {}
        packaging_details = {}
        sno = 1
        
        print("\nEnter items (type 'STOP' or '0' when done):")
        while True:
            code = self._get_valid_code()
            if code in ["STOP", "0", ""]:
                break
                
            quantity = self._get_quantity()
            if quantity == 0:
                continue
                
            item_data = self._process_item(
                code, quantity, sno, 
                bill_items, total_weight, packaging_details
            )
            if item_data:
                bill_items.append(item_data)
                sno += 1
        
        if not bill_items:
            return None
            
        total, final_bill = self._calculate_total(bill_items, total_weight)
        return {
            "items": final_bill,
            "total": total,
            "packaging": packaging_details,
            "phone": phone
        }

    def display_bill(self, bill_data):
        """Display the bill in console based on selected format."""
        headers = self._get_headers()
        display_data = self._format_bill_data(bill_data["items"])
        
        print("\n" + "=" * settings.WIDTH)
        print("FINAL BILL".center(settings.WIDTH))
        print("=" * settings.WIDTH)
        print(tabulate(display_data, headers=headers, tablefmt="fancy_grid"))
        print(f"\nTOTAL: ₹{bill_data['total']}".rjust(settings.WIDTH - 10))

    def finalize_bill(self, bill_data, payment_mode, discount=0):
        """
        Save bill to Excel and process payment.
        
        Args:
            bill_data: Bill data dictionary
            payment_mode: 1 for Cash, 2 for Digital
            discount: Discount amount (default 0)
            
        Returns:
            str: Generated bill number
        """
        bill_number = self._save_to_excel(bill_data, payment_mode, discount)
        
        if bill_data["phone"]:
            self.customers.update_customer(
                bill_data["phone"],
                bill_data["total"] - discount,
                bill_number
            )
        
        self._update_accounts(payment_mode, bill_data["total"], discount)
        return bill_number

    def send_whatsapp_bill(self, bill_data, bill_number, discount=0):
        """Send formatted bill via WhatsApp."""
        message = self._prepare_whatsapp_message(bill_data, bill_number, discount)
        image_to_clipboard(settings.LOGO_IMAGE)
        open_whatsapp(bill_data["phone"])
        
        # Paste image and message
        pyperclip.copy(message)
        sleep(1)
        hotkey("ctrl", "v")
        sleep(0.5)
        press("enter")
        
        close_browser_tab()

    def _get_valid_code(self):
        """Get valid item code from user."""
        while True:
            code = input("Enter Item Code: ").upper().strip()
            if code in ["STOP", "0", ""]:
                return code
            if code in self.inventory.keys:
                return code
            print("Invalid code! Try again.")

    def _get_quantity(self):
        """Get valid quantity from user."""
        while True:
            try:
                qty = int(input("Enter Quantity: "))
                return max(0, qty)
            except ValueError:
                print("Invalid quantity! Enter a number.")

    def _process_item(self, code, quantity, sno, bill_items, total_weight, packaging_details):
        """Process an item for billing."""
        item = self.inventory.stock[code]
        item_name = item[0]
        size = item[1]
        price = item[4]
        
        # Check stock
        stock_left = item[-2] - quantity
        if stock_left < 0:
            if not self._handle_stock_error(stock_left):
                return None
        
        # Update packaging details
        if item_name not in packaging_details:
            packaging_details[item_name] = []
        packaging_details[item_name].append(f"{size}GM x {quantity}")
        
        # Update total weight
        if item_name not in total_weight:
            total_weight[item_name] = 0
        total_weight[item_name] += size * quantity
        
        # Update sales in Excel
        sale_cell = self._get_sale_cell(code)
        self.sales_sheet[sale_cell] = self.sales_sheet[sale_cell].value + f"+{quantity}"
        
        # Return item data based on bill format
        if self.bill_format == "Compact":
            return [sno, item_name, f"{size}GM", quantity, price * quantity]
        elif self.bill_format == "Detailed":
            return [sno, item_name, f"{size}GM", price, quantity, price * quantity]
        else:  # Full
            return [sno, code, item_name, f"{size}GM", item[3], price, quantity, price * quantity]

    def _handle_stock_error(self, stock_left):
        """Handle stock shortage situations."""
        if stock_left == 0:
            print("Alert! Stock will be empty after this sale.")
        else:
            print(f"Alert! Stock will be negative ({stock_left}) after this sale.")
        
        while True:
            choice = input("Proceed anyway? (y/n): ").lower()
            if choice == 'y':
                return True
            elif choice == 'n':
                return False
            print("Invalid choice!")

    def _get_sale_cell(self, code):
        """Get cell address for sales column."""
        for row in range(2, self.sales_sheet.max_row + 1):
            if self.sales_sheet[f"C{row}"].value == code:
                return f"J{row}"
        raise ValueError(f"Item code {code} not found in sales sheet")

    def _calculate_total(self, bill_items, total_weight):
        """Calculate bill total and format final bill."""
        total = sum(item[-1] for item in bill_items if isinstance(item[0], int))
        
        # Add total row
        if self.bill_format == "Compact":
            bill_items.append(["", "", "TOTAL", "", total])
        elif self.bill_format == "Detailed":
            bill_items.append(["", "", "", "TOTAL", "", total])
        else:  # Full
            bill_items.append(["", "", "", "", "", "", "TOTAL", total])
        
        return total, bill_items

    def _get_headers(self):
        """Get headers based on bill format."""
        if self.bill_format == "Compact":
            return ["S.No.", "Item", "Size", "Qty", "Amount"]
        elif self.bill_format == "Detailed":
            return ["S.No.", "Item", "Size", "Rate", "Qty", "Amount"]
        else:  # Full
            return ["S.No.", "Code", "Item", "Size", "MRP", "Rate", "Qty", "Amount"]

    def _format_bill_data(self, items):
        """Format bill data for display."""
        return [item for item in items if isinstance(item[0], int)]

    def _save_to_excel(self, bill_data, payment_mode, discount):
        """Save bill data to Excel."""
        bill_number = f"{settings.BILL_CODE}{self.customers.increment_bill_counter()}"
        
        # Add bill header
        self.bills_sheet.append([f"Bill No: {bill_number}"])
        self.bills_sheet.append([f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}"])
        if bill_data["phone"]:
            self.bills_sheet.append([f"Phone: {bill_data['phone']}"])
        
        # Add column headers
        headers = self._get_headers()
        self.bills_sheet.append(headers)
        
        # Add items
        for item in bill_data["items"]:
            if isinstance(item[0], int):
                self.bills_sheet.append(item)
        
        # Add totals
        self.bills_sheet.append([])
        self.bills_sheet.append(["", "", "Subtotal:", bill_data["total"]])
        if discount:
            self.bills_sheet.append(["", "", "Discount:", discount])
            self.bills_sheet.append(["", "", "Total:", bill_data["total"] - discount])
        
        # Add payment mode
        payment_text = "Cash" if payment_mode == 1 else "Digital"
        self.bills_sheet.append(["", "", "Payment Mode:", payment_text])
        
        # Save packaging details as comments
        self._add_packaging_comments(bill_data["packaging"])
        
        self.workbook.save(settings.EXCEL_FILE)
        return bill_number

    def _add_packaging_comments(self, packaging_details):
        """Add packaging details as Excel comments."""
        for row in range(1, self.bills_sheet.max_row + 1):
            item_name = self.bills_sheet[f"B{row}"].value
            if item_name in packaging_details:
                comment = Comment("\n".join(packaging_details[item_name]), "InvenGo")
                self.bills_sheet[f"D{row}"].comment = comment

    def _update_accounts(self, mode, amount, discount):
        """Update accounts sheet with payment."""
        if mode == 1:  # Cash
            self.accounts_sheet["B2"] = self.accounts_sheet["B2"].value + f"+{amount}"
            if discount:
                self.accounts_sheet["B4"] = self.accounts_sheet["B4"].value + f"+{discount}"
        else:  # Digital
            self.accounts_sheet["B3"] = self.accounts_sheet["B3"].value + f"+{amount}"
            if discount:
                self.accounts_sheet["B5"] = self.accounts_sheet["B5"].value + f"+{discount}"
        self.workbook.save(settings.EXCEL_FILE)

    def _prepare_whatsapp_message(self, bill_data, bill_number, discount):
        """Format WhatsApp message based on selected style."""
        if self.whatsapp_format == "Simple":
            return self._simple_whatsapp_format(bill_data, bill_number, discount)
        elif self.whatsapp_format == "Detailed":
            return self._detailed_whatsapp_format(bill_data, bill_number, discount)
        else:
            return self._professional_whatsapp_format(bill_data, bill_number, discount)

    def _simple_whatsapp_format(self, bill_data, bill_number, discount):
        """Basic WhatsApp message format."""
        message = [
            f"*{settings.BILL_CODE} BILL #{bill_number}*",
            f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "\nITEMS:"
        ]
        
        for item in bill_data["items"]:
            if isinstance(item[0], int):
                message.append(
                    f"{item[0]}. {item[1]} - {item[2]} x {item[3]} = ₹{item[4]}"
                )
        
        message.extend([
            f"\n*Total: ₹{bill_data['total']}*",
            f"*Discount: ₹{discount}*" if discount else "",
            f"*Final Amount: ₹{bill_data['total'] - discount}*",
            "\nThank you for your purchase!"
        ])
        
        return "\n".join(filter(None, message))

    def _detailed_whatsapp_format(self, bill_data, bill_number, discount):
        """More detailed WhatsApp format with packaging info."""
        message = [
            f"*{settings.BILL_CODE} BILL #{bill_number}*",
            f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "\nITEM DETAILS:"
        ]
        
        for item in bill_data["items"]:
            if isinstance(item[0], int):
                packaging = ", ".join(bill_data["packaging"].get(item[1], []))
                message.extend([
                    f"\n*{item[0]}. {item[1]}*",
                    f"Size: {item[2]}",
                    f"Rate: ₹{item[3]}" if len(item) > 4 else "",
                    f"Qty: {item[-2]} ({packaging})",
                    f"Amount: ₹{item[-1]}"
                ])
        
        message.extend([
            f"\n*Subtotal: ₹{bill_data['total']}*",
            f"*Discount: ₹{discount}*" if discount else "",
            f"*Final Amount: ₹{bill_data['total'] - discount}*",
            "\nWe appreciate your business!",
            "\nFor feedback: https://example.com/feedback"
        ])
        
        return "\n".join(filter(None, message))

    def _professional_whatsapp_format(self, bill_data, bill_number, discount):
        """Professional format with company branding."""
        message = [
            f"*{settings.BILL_CODE}*  •  INVOICE #{bill_number}",
            f"*Date:* {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            "\n--------------------------------",
            "*ITEMIZED BILL*"
        ]
        
        for item in bill_data["items"]:
            if isinstance(item[0], int):
                packaging = "\n      ".join(bill_data["packaging"].get(item[1], []))
                message.extend([
                    f"\n*{item[0]}. {item[1]}*",
                    f"      Code: {item[1]}" if self.include_full_details else "",
                    f"      Size: {item[2]}",
                    f"      Rate: ₹{item[3]}" if len(item) > 4 else "",
                    f"      Qty: {item[-2]}",
                    f"      Packaging: {packaging}" if packaging else "",
                    f"      Amount: ₹{item[-1]}"
                ])
        
        message.extend([
            "\n--------------------------------",
            f"*SUBTOTAL:* ₹{bill_data['total']}",
            f"*DISCOUNT:* ₹{discount}" if discount else "",
            f"*TOTAL DUE:* ₹{bill_data['total'] - discount}",
            "\nThank you for choosing us!",
            "\n*Contact:* support@invengo.com",
            "*Website:* https://invengo.example.com"
        ])
        
        return "\n".join(filter(None, message))