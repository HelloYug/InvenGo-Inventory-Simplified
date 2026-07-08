from openpyxl import load_workbook

class AccountsManager:
    def __init__(self, workbook):
        """
        Initialize accounts manager with Excel workbook.
        
        Args:
            workbook: OpenPyXL Workbook object
        """
        self.workbook = workbook
        self.sheet = workbook["Accounts"]
        
    def get_sales_summary(self):
        """Get total sales summary."""
        return {
            "cash_sale": self._eval_cell("B2"),
            "digital_sale": self._eval_cell("B3"),
            "cash_discount": self._eval_cell("B4"),
            "digital_discount": self._eval_cell("B5")
        }
    
    def add_expense(self, amount, description):
        """
        Add new expense to accounts.
        
        Args:
            amount: Expense amount
            description: Expense description
        """
        row = 4  # Starting row for expenses
        while self.sheet[f"G{row}"].value is not None:
            row += 1
            
        self.sheet[f"G{row}"] = amount
        self.sheet[f"H{row}"] = description
    
    def update_payment(self, mode, amount, discount=0):
        """
        Update payment records.
        
        Args:
            mode: 1 for Cash, 2 for Digital
            amount: Payment amount
            discount: Discount amount (default 0)
        """
        if mode == 1:  # Cash
            self.sheet["B2"] = self.sheet["B2"].value + f"+{amount}"
            if discount:
                self.sheet["B4"] = self.sheet["B4"].value + f"+{discount}"
        elif mode == 2:  # Digital
            self.sheet["B3"] = self.sheet["B3"].value + f"+{amount}"
            if discount:
                self.sheet["B5"] = self.sheet["B5"].value + f"+{discount}"
    
    def _eval_cell(self, cell_ref):
        """Evaluate formula cell safely."""
        try:
            return eval(self.sheet[cell_ref].value[1:])
        except:
            return 0