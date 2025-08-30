import os
import sys
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

print("Script started (after imports)")

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

# Layout config object
LAYOUT = {
    "page": {"w": 419.25, "h": 595.5},
    "margins": {"L": 24, "R": 24, "B": 24, "top_band": 20},
    "content": {
        "x": 24,
        "y_top": 20,
        "w": 371.25,
        "h": 555.5
    },
    "typography": {
        "title": {"font": "Argent", "size": 25, "min_size": 18, "color": "#aa8600"},
        "name": {"font": "Argent", "size": 17, "min_size": 12, "color": "#000000"},
        "desc": {"font": "Argent", "size": 12, "min_size": 10, "color": "#000000"},
        "desc_line_height": 14.5
    },
    "spacing": {
        "title_break_after": 8,
        "name_line": 15,
        "desc_line": 8,
        "dish_gap": 10,
        "category_gap": 14,
        "first_baseline_y_top": 110
    },
    "max_width": 371.25
}

def top_to_rl_y(y_top):
    return LAYOUT["page"]["h"] - y_top


def load_data():
    if not os.path.exists(DATA_FILE):
        print(f"Bot: Error! '{DATA_FILE}' not found in {os.getcwd()}.")
        print("Please make sure menu_data.xlsx exists in the project directory.")
        sys.exit(1)
    try:
        df = pd.read_excel(DATA_FILE)
    except Exception as e:
        print(f"Bot: Error reading '{DATA_FILE}': {e}")
        sys.exit(1)
    return df


def get_categories(df):
    return sorted(df['Category'].unique())


def parse_command(command, available_dishes):
    if not command.startswith('/menu'):
        return None, 'Bot: Unknown command. Use /menu <dish names>'
    rest = command[len('/menu'):].strip()
    if not rest:
        return None, 'Bot: Please specify dish names. Example: /menu Rosół, Schabowy, Sernik'
    # Support comma-separated dish names
    requested = [dish.strip() for dish in rest.split(',') if dish.strip()]
    wrong = [dish for dish in requested if dish not in available_dishes]
    if wrong:
        return None, f"Bot: Unknown dish: {', '.join(wrong)}. Available: {', '.join(available_dishes)}"
    return requested, None


def register_fonts():
    if not os.path.exists(FONT_FILE):
        print(f"Bot: Error! Font '{FONT_FILE}' not found in {os.getcwd()}.")
        print("Please make sure Argent.ttf exists in the 'fonts' folder and is a valid TTF font.")
        sys.exit(1)
    try:
        pdfmetrics.registerFont(TTFont(CATEGORY_FONT, FONT_FILE, subfontIndex=0, uni=True))
    except TypeError:
        try:
            pdfmetrics.registerFont(TTFont(CATEGORY_FONT, FONT_FILE))
        except Exception as e:
            print(f"Bot: Error registering font '{FONT_FILE}': {e}")
            print("Make sure the font is a valid TrueType TTF file, not OTF/CFF.")
            sys.exit(1)



# --- New generate_pdf using layout system ---
def generate_pdf(df, selected_dishes):
    c = canvas.Canvas(OUTPUT_FILE, pagesize=(LAYOUT["page"]["w"], LAYOUT["page"]["h"]))
    width, height = LAYOUT["page"]["w"], LAYOUT["page"]["h"]
    # Draw background
    if os.path.exists(BG_FILE):
        bg = ImageReader(BG_FILE)
        c.drawImage(bg, 0, 0, width=width, height=height)
    else:
        print(f"Bot: Warning! Background '{BG_FILE}' not found.")

    # Start at first title baseline (top-left coordinates)
    y_top = LAYOUT["spacing"]["first_baseline_y_top"]



    from reportlab.pdfbase.pdfmetrics import stringWidth
    content_x = LAYOUT["content"]["x"]
    content_w = LAYOUT["content"]["w"]

    def draw_centered_unicode(c, x, y, text, font, size):
        text = str(text)
        text_width = stringWidth(text, font, size)
        draw_x = x + (content_w - text_width) / 2
        # Use TextObject for Unicode
        text_obj = c.beginText()
        text_obj.setTextOrigin(draw_x, y)
        text_obj.setFont(font, size)
        text_obj.textLine(text)
        c.drawText(text_obj)

    # Find dish rows in the order entered
    dish_rows = [df[df['Name'] == dish].iloc[0] for dish in selected_dishes]
    # Group by category, preserving order
    from collections import OrderedDict
    category_to_dishes = OrderedDict()
    for row in dish_rows:
        cat = row['Category']
        if cat not in category_to_dishes:
            category_to_dishes[cat] = []
        category_to_dishes[cat].append(row)

    for cat, dishes in category_to_dishes.items():
        # Category Title
        title_font = LAYOUT["typography"]["title"]["font"]
        title_size = LAYOUT["typography"]["title"]["size"]
        title_color = LAYOUT["typography"]["title"]["color"]
        c.setFillColor(HexColor(title_color))
        y_rl = top_to_rl_y(y_top)
        draw_centered_unicode(c, content_x, y_rl, cat, title_font, title_size)
        print(f"Bot: Adding category: {cat}")
        y_top += LAYOUT["spacing"]["title_break_after"] + LAYOUT["spacing"]["title_line"] if "title_line" in LAYOUT["spacing"] else 28

        for row in dishes:
            # Dish Name
            name_font = LAYOUT["typography"]["name"]["font"]
            name_size = LAYOUT["typography"]["name"]["size"]
            name_color = LAYOUT["typography"]["name"]["color"]
            c.setFillColor(HexColor(name_color))
            name_text = str(row['Name'])
            y_rl = top_to_rl_y(y_top)
            draw_centered_unicode(c, content_x, y_rl, name_text, name_font, name_size)
            print(f"Bot: Adding dish: {row['Name']}")
            y_top += LAYOUT["spacing"]["name_line"]

            # Description (wrap if needed)
            desc_font = LAYOUT["typography"]["desc"]["font"]
            desc_size = LAYOUT["typography"]["desc"]["size"]
            desc_color = LAYOUT["typography"]["desc"]["color"]
            c.setFillColor(HexColor(desc_color))
            desc_text = str(row['Description'])
            max_width = LAYOUT["max_width"] - 40  # indent for description
            words = desc_text.split()
            lines = []
            line = ""
            for word in words:
                test_line = line + (" " if line else "") + word
                if stringWidth(test_line, desc_font, desc_size) > max_width:
                    if line:
                        lines.append(line)
                    line = word
                else:
                    line = test_line
            if line:
                lines.append(line)
            for desc_line in lines:
                y_rl = top_to_rl_y(y_top)
                draw_centered_unicode(c, content_x, y_rl, desc_line, desc_font, desc_size)
                print(f"Bot: Adding description: {desc_line}")
                y_top += LAYOUT["typography"]["desc_line_height"]

            y_top += LAYOUT["spacing"]["dish_gap"]

        y_top += LAYOUT["spacing"]["category_gap"]

    c.save()
    print(f"Bot: Menu ready! Saved as {OUTPUT_FILE}")


def main():
    print("Welcome to MenuBot 📝")
    print("Type your request like in Telegram:")
    print("Example: /menu Rosół, Schabowy, Sernik\n")
    print("[DEBUG] Loading data...")
    df = load_data()
    print("[DEBUG] Data loaded. Available dishes:", list(df['Name']))
    available_dishes = list(df['Name'])
    print("[DEBUG] Registering fonts...")
    register_fonts()
    print("[DEBUG] Fonts registered. Entering command loop.")
    try:
        while True:
            print("[DEBUG] Waiting for user input...")
            command = input("You: ")
            print(f"[DEBUG] Command entered: {command}")
            selected_dishes, error = parse_command(command, available_dishes)
            print(f"[DEBUG] Selected dishes: {selected_dishes}, Error: {error}")
            if error:
                print(error)
                continue
            print(f"Bot: Got it! Generating menu with dishes: {', '.join(selected_dishes)}")
            generate_pdf(df, selected_dishes)
            break
    except Exception as e:
        print(f"[DEBUG] Exception in main loop: {e}")

if __name__ == '__main__':
    print("About to run main()")
    main()
