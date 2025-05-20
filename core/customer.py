class CustomerManager:
    def __init__(self, workbook):
        self.workbook = workbook
        self.sheet = workbook["Customer Data"]
        self.bill_counter = self._get_bill_counter()
        
    def _get_bill_counter(self):
        """Get current bill counter value"""
        return int(eval(self.sheet["I1"].value[1:]))
    
    def get_customer(self, phone):
        """Find customer by phone number"""
        row = 3
        while self.sheet[f"A{row}"].value is not None:
            if str(self.sheet[f"A{row}"].value) == str(phone):
                return {
                    "row": row,
                    "total": eval(self.sheet[f"B{row}"].value[1:]),
                    "bills": self.sheet[f"C{row}"].value.split() if self.sheet[f"C{row}"].value else []
                }
            row += 1
        return None
    
    def update_customer(self, phone, amount, bill_number):
        """Update customer record with new purchase"""
        customer = self.get_customer(phone)
        if customer:
            # Update existing customer
            self.sheet[f"B{customer['row']}"] = self.sheet[f"B{customer['row']}"].value + f"+{amount}"
            bills = customer['bills'] + [bill_number]
            self.sheet[f"C{customer['row']}"] = " ".join(bills)
        else:
            # Add new customer
            row = 3
            while self.sheet[f"A{row}"].value is not None:
                row += 1
            self.sheet[f"A{row}"] = phone
            self.sheet[f"B{row}"] = f"={amount}"
            self.sheet[f"C{row}"] = bill_number
    
    def increment_bill_counter(self):
        """Increment and return next bill number"""
        self.bill_counter += 1
        self.sheet["I1"] = f"={self.bill_counter}"
        return format_number(self.bill_counter, 4)