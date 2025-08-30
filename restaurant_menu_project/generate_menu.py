import os
import sys
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8283708069:AAE-a2JilzOQkvVlkTivA5HFxVmwo4PDRFc"

# Constants
DATA_FILE = 'menu_data.xlsx'
BG_FILE = os.path.join('restaurant_menu_project', 'menu_background.png')
FONT_FILE = os.path.join('fonts', 'Argent.ttf')
OUTPUT_FILE = 'menu_output.png'
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
        "y_top": 50,
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
        "name_line": 25,
        "desc_line": 15,
        "dish_gap": 10,
        "category_gap": 10,
        "first_baseline_y_top": 110
    },
    "max_width": 371.25,
    "vertical_align": "middle",  # can be "top" or "middle"
    "middle_y": None  # if set, overrides automatic centering
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


def get_font(size):
    if not os.path.exists(FONT_FILE):
        print(f"Bot: Error! Font '{FONT_FILE}' not found in {os.getcwd()}.")
        print("Please make sure Argent.ttf exists in the 'fonts' folder and is a valid TTF font.")
        sys.exit(1)
    return ImageFont.truetype(FONT_FILE, size)




# --- New generate_png using Pillow ---
def generate_png(df, selected_dishes):
    # Use background image size for output
    if os.path.exists(BG_FILE):
        bg = Image.open(BG_FILE).convert("RGBA")
        width, height = bg.size
        img = bg.copy()
    else:
        width, height = int(LAYOUT["page"]["w"]), int(LAYOUT["page"]["h"])
        img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Scale layout to match background size
    layout_scale_x = width / LAYOUT["page"]["w"]
    layout_scale_y = height / LAYOUT["page"]["h"]
    content_x = int(LAYOUT["content"]["x"] * layout_scale_x)
    content_w = int(LAYOUT["content"]["w"] * layout_scale_x)

    # Scale font sizes and spacing
    def get_scaled_font(size):
        return get_font(int(size * layout_scale_y))

    def draw_centered_unicode(draw, x, y, text, font, fill):
        text = str(text)
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        draw_x = x + (content_w - text_width) / 2
        draw.text((draw_x, y), text, font=font, fill=fill)

    # Find dish rows in the order entered
    dish_rows = [df[df['Name'] == dish].iloc[0] for dish in selected_dishes]
    from collections import OrderedDict
    category_to_dishes = OrderedDict()
    for row in dish_rows:
        cat = row['Category']
        if cat not in category_to_dishes:
            category_to_dishes[cat] = []
        category_to_dishes[cat].append(row)

    # Calculate total height needed for menu
    total_height = 0
    scaled_title_break_after = LAYOUT["spacing"]["title_break_after"] * layout_scale_y
    scaled_title_line = LAYOUT["spacing"].get("title_line", 28) * layout_scale_y
    scaled_name_line = LAYOUT["spacing"]["name_line"] * layout_scale_y
    scaled_desc_line_height = LAYOUT["typography"]["desc_line_height"] * layout_scale_y
    scaled_dish_gap = LAYOUT["spacing"]["dish_gap"] * layout_scale_y
    scaled_category_gap = LAYOUT["spacing"]["category_gap"] * layout_scale_y
    scaled_max_width = (LAYOUT["max_width"] - 40) * layout_scale_x
    for cat, dishes in category_to_dishes.items():
        total_height += scaled_title_break_after
        total_height += scaled_title_line
        for row in dishes:
            total_height += scaled_name_line
            desc_text = str(row['Description'])
            words = desc_text.split()
            lines = []
            line = ""
            font = get_scaled_font(LAYOUT["typography"]["desc"]["size"])
            for word in words:
                test_line = line + (" " if line else "") + word
                bbox = font.getbbox(test_line)
                test_width = bbox[2] - bbox[0]
                if test_width > scaled_max_width:
                    if line:
                        lines.append(line)
                    line = word
                else:
                    line = test_line
            if line:
                lines.append(line)
            total_height += len(lines) * scaled_desc_line_height
            total_height += scaled_dish_gap
        total_height += scaled_category_gap

    # Determine starting y_top for vertical alignment
    if LAYOUT.get("vertical_align") == "middle":
        content_h = LAYOUT["content"]["h"] * layout_scale_y
        top_margin = LAYOUT["content"]["y_top"] * layout_scale_y
        if LAYOUT.get("middle_y") is not None:
            y_top = max(top_margin, LAYOUT["middle_y"] * layout_scale_y - total_height / 2)
        else:
            y_top = top_margin + max(0, (content_h - total_height) / 2)
    else:
        y_top = LAYOUT["spacing"]["first_baseline_y_top"] * layout_scale_y

    for cat, dishes in category_to_dishes.items():
        # Category Title
        title_font = get_scaled_font(LAYOUT["typography"]["title"]["size"])
        title_color = LAYOUT["typography"]["title"]["color"]
        y_draw = y_top
        draw_centered_unicode(draw, content_x, y_draw, cat, title_font, title_color)
        y_top += scaled_title_break_after + scaled_title_line

        for row in dishes:
            # Dish Name
            name_font = get_scaled_font(LAYOUT["typography"]["name"]["size"])
            name_color = LAYOUT["typography"]["name"]["color"]
            name_text = str(row['Name'])
            y_draw = y_top
            draw_centered_unicode(draw, content_x, y_draw, name_text, name_font, name_color)
            y_top += scaled_name_line

            # Description (wrap if needed)
            desc_font = get_scaled_font(LAYOUT["typography"]["desc"]["size"])
            desc_color = LAYOUT["typography"]["desc"]["color"]
            desc_text = str(row['Description'])
            words = desc_text.split()
            lines = []
            line = ""
            for word in words:
                test_line = line + (" " if line else "") + word
                bbox = desc_font.getbbox(test_line)
                test_width = bbox[2] - bbox[0]
                if test_width > scaled_max_width:
                    if line:
                        lines.append(line)
                    line = word
                else:
                    line = test_line
            if line:
                lines.append(line)
            for desc_line in lines:
                y_draw = y_top
                draw_centered_unicode(draw, content_x, y_draw, desc_line, desc_font, desc_color)
                y_top += scaled_desc_line_height

            y_top += scaled_dish_gap

        y_top += scaled_category_gap

    # Save as PNG with maximum quality, no compression loss
    img.save(OUTPUT_FILE, format="PNG", optimize=True)
    print(f"Bot: Menu ready! Saved as {OUTPUT_FILE} (PNG, max quality)")



# --- Telegram Bot Handlers ---
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    df = load_data()
    available_dishes = list(df['Name'])
    command = update.message.text
    selected_dishes, error = parse_command(command, available_dishes)
    if error:
        await update.message.reply_text(error)
        return
    await update.message.reply_text(f"Bot: Got it! Generating menu with dishes: {', '.join(selected_dishes)}")
    generate_png(df, selected_dishes)
    # Send PNG file
    with open(OUTPUT_FILE, "rb") as png_file:
        await update.message.reply_photo(png_file, filename=OUTPUT_FILE)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to MenuBot 📝\nSend /menu followed by dish names separated by commas.\nExample: /menu Rosół, Schabowy, Sernik"
    )

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Regex(r"^/menu.*"), menu_command))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
