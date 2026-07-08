from openpyxl import load_workbook
from openpyxl.comments import Comment
from tabulate import tabulate
import pyperclip
from time import sleep
import win32clipboard
from io import BytesIO
from PIL import Image
import webbrowser
from pyautogui import hotkey, press
from win32gui import GetWindowText, GetForegroundWindow

def format_number(number, digits):
    """Format number with leading zeros"""
    str_num = str(number)
    return str_num.zfill(digits)

def image_to_clipboard(image_path):
    """Copy image to clipboard for WhatsApp sharing"""
    image = Image.open(image_path)
    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()
    
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

def open_whatsapp(phone):
    """Open WhatsApp Web with customer number"""
    webbrowser.open(f"https://wa.me/91{phone}")
    sleep(5)

def close_browser_tab():
    """Close the current browser tab"""
    sleep(0.1)
    hotkey("ctrl", "w")
    sleep(0.1)
    hotkey("super", "t")
    press("right", 9, 0.02)
    press("enter")