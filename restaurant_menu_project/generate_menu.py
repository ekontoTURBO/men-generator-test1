import os
import sys
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

# Constants
DATA_FILE = 'menu_data.xlsx'
BG_FILE = 'menu_background.png'
FONT_FILE = os.path.join('fonts', 'Argent.ttf')
OUTPUT_FILE = 'menu_output.pdf'
CATEGORY_COLOR = '#aa8600'
CATEGORY_SIZE = 25
NAME_SIZE = 17
DESC_SIZE = 12
NAME_COLOR = '#000000'
DESC_COLOR = '#000000'
CATEGORY_FONT = 'Argent'
NAME_FONT = 'Argent'
DESC_FONT = 'Argent'
CATEGORY_SPACING = 30
DISH_SPACING = 40
NAME_DESC_SPACING = 15


def load_data():
    if not os.path.exists(DATA_FILE):
        print(f"Bot: Error! '{DATA_FILE}' not found.")
        sys.exit(1)
    df = pd.read_excel(DATA_FILE)
    return df


def get_categories(df):
    return sorted(df['Category'].unique())


def parse_command(command, available_categories):
    if not command.startswith('/menu'):
        return None, 'Bot: Unknown command. Use /menu <categories>'
    parts = command.strip().split()
    if len(parts) < 2:
        return None, 'Bot: Please specify categories. Example: /menu Soup Dessert'
    if parts[1].lower() == 'all':
        return available_categories, None
    requested = parts[1:]
    wrong = [cat for cat in requested if cat not in available_categories]
    if wrong:
        return None, f"Bot: Unknown category: {', '.join(wrong)}. Available: {', '.join(available_categories)}"
    return requested, None


def register_fonts():
    if not os.path.exists(FONT_FILE):
        print(f"Bot: Error! Font '{FONT_FILE}' not found.")
        sys.exit(1)
    pdfmetrics.registerFont(TTFont(CATEGORY_FONT, FONT_FILE))


def generate_pdf(df, categories):
    c = canvas.Canvas(OUTPUT_FILE, pagesize=A4)
    width, height = A4
    # Draw background
    if os.path.exists(BG_FILE):
        bg = ImageReader(BG_FILE)
        c.drawImage(bg, 0, 0, width=width, height=height)
    else:
        print(f"Bot: Warning! Background '{BG_FILE}' not found.")
    y = height - 60
    for cat in categories:
        c.setFont(CATEGORY_FONT, CATEGORY_SIZE)
        c.setFillColor(HexColor(CATEGORY_COLOR))
        c.drawString(60, y, cat)
        print(f"Bot: Adding category: {cat}")
        y -= CATEGORY_SPACING
        dishes = df[df['Category'] == cat]
        for _, row in dishes.iterrows():
            c.setFont(NAME_FONT, NAME_SIZE)
            c.setFillColor(HexColor(NAME_COLOR))
            c.drawString(80, y, str(row['Name']))
            print(f"Bot: Adding dish: {row['Name']}")
            y -= NAME_DESC_SPACING
            c.setFont(DESC_FONT, DESC_SIZE)
            c.setFillColor(HexColor(DESC_COLOR))
            c.drawString(100, y, str(row['Description']))
            print(f"Bot: Adding description: {row['Description']}")
            y -= DISH_SPACING
        y -= CATEGORY_SPACING
    c.save()
    print(f"Bot: Menu ready! Saved as {OUTPUT_FILE}")


def main():
    print("Welcome to MenuBot 📝")
    print("Type your request like in Telegram:")
    print("Example: /menu Soup Main Dish Dessert\n")
    df = load_data()
    available_categories = get_categories(df)
    register_fonts()
    while True:
        command = input("You: ")
        categories, error = parse_command(command, available_categories)
        if error:
            print(error)
            continue
        print(f"Bot: Got it! Generating menu with categories: {', '.join(categories)}")
        generate_pdf(df, categories)
        break

if __name__ == '__main__':
    main()
