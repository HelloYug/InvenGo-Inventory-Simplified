"""
InvenGo Core Modules
====================

This package contains all core functionality for the inventory management system.
"""

from .inventory import InventoryManager
from .billing import BillingSystem
from .customer import CustomerManager
from .accounts import AccountsManager
from .utils import (
    format_number,
    image_to_clipboard,
    open_whatsapp,
    close_browser_tab
)

__all__ = [
    'InventoryManager',
    'BillingSystem',
    'CustomerManager',
    'AccountsManager',
    'format_number',
    'image_to_clipboard',
    'open_whatsapp',
    'close_browser_tab'
]