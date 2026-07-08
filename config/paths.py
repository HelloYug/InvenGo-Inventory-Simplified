from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
ASSETS_DIR = BASE_DIR / "assets"

# File paths
EXCEL_TEMPLATE = TEMPLATES_DIR / "template.xlsx"
LOGO_IMAGE = ASSETS_DIR / "logo.png"