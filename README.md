# 🧾 InvenGo — Inventory Simplified

A comprehensive inventory and billing management system for small businesses with WhatsApp integration.

---

## 📦 Features

- 📊 **Inventory Management**
  - Categorized stock viewing (Spices, Dry Fruits, Seeds, Tea)
  - Real-time stock updates
  - Add new items and categories

- 🧾 **Flexible Billing**
  - Multiple bill formats (Compact/Detailed/Full)
  - Cash and digital payment tracking
  - Discount management

- 📱 **WhatsApp Integration**
  - Multiple message formats (Simple/Detailed/Professional)
  - Automatic bill sharing with logo
  - Packaging details included

- 📈 **Reporting**
  - Sales summaries (Cash/Digital)
  - Expense tracking
  - Customer purchase history

---

## 🏗️ Project Structure

```
InvenGo/
├── main.py               # Main application entry point
├── config/               # Configuration files
│   ├── paths.py          # File path configurations
│   └── settings.py       # Application settings
├── core/                 # Core functionality
│   ├── __init__.py       # Package initialization
│   ├── inventory.py      # Inventory management
│   ├── billing.py        # Billing system
│   ├── customer.py       # Customer management
│   ├── accounts.py       # Financial tracking
│   └── utils.py          # Utility functions
├── templates/            # Excel templates
│   └── template.xlsx     # Main data file
├── assets/               # Static assets
│   └── logo.jpg          # Logo for WhatsApp bills
├── requirements.txt      # Python dependencies
└── README.md             # Documentation
```

---

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/HelloYug/InvenGo-Inventory-Simplified.git
   cd InvenGo
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the system**
   - Place your logo in `assets/logo.png`
   - Update `config/paths.py` if using custom file locations
   - Prepare your Excel template (see `templates/template.xlsx`)

4. **Run the application**
   ```bash
   python main.py
   ```

---

## 🖥️ Usage

1. **Main Menu Options**
   ```
   1. Show Stock
   2. Billing
   3. Show Price
   4. Total Sales / Accounts
   5. Add Expenses
   6. Add New Item
   7. Add Stock
   8. Show/Send Bill
   9. Exit
   ```

2. **Billing Process**
   - Select bill format and WhatsApp style
   - Add items by code
   - Apply discounts if needed
   - Choose payment method (Cash/Digital)
   - Optionally send via WhatsApp

---

## 📊 Excel Template Structure

The system uses an Excel file with these sheets:

1. **Sales & Stocks** - Product inventory
2. **Bills** - Complete bill records
3. **Accounts** - Financial tracking
4. **Customer Data** - Purchase history

---

## 📝 Requirements

- Python 3.8+
- Packages:
  - `openpyxl` (Excel handling)
  - `tabulate` (Console tables)
  - `pyautogui` (WhatsApp automation)
  - `Pillow` (Image handling)
  - `pywin32` (Windows clipboard)

Install all with:

   ```bash
   pip install -r requirements.txt
   ```

---

## 📜 License

MIT License - Free for personal and commercial use.

---

## 👨‍💻 Author

**Yug Agarwal**
- 📧 [yugagarwal704@gmail.com](mailto:yugagarwal704@gmail.com)
- 🔗 GitHub – [@HelloYug](https://github.com/HelloYug)
