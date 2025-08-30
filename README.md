
# Restaurant Menu Telegram Bot

This project generates a restaurant menu as a PNG image and sends it to users via Telegram using a bot.

## Features
- Users interact with the bot on Telegram.
- Send `/menu dish1, dish2, dish3` to receive a custom menu image.
- Menu is generated using data from `menu_data.xlsx` and styled with a background image and custom font.
- All text is centered and formatted according to print-safe rules.
- Dishes are grouped by category, with category titles shown once above their dishes.
- Customizable layout and typography via the `LAYOUT` config in `generate_menu.py`.

## Setup Instructions

### 1. Requirements
- Python 3.8+
- Telegram Bot Token
- The following Python packages:
   - python-telegram-bot
   - Pillow
   - pandas
   - openpyxl

### 2. Files Needed
- `restaurant_menu_project/generate_menu.py` (main script)
- `restaurant_menu_project/menu_data.xlsx` (menu data)
- `restaurant_menu_project/menu_background.png` (background image)
- `restaurant_menu_project/fonts/Argent.ttf` (font file)

### 3. Installation
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install python-telegram-bot Pillow pandas openpyxl
```

### 4. Running the Bot
```bash
python restaurant_menu_project/generate_menu.py
```
- The bot will start and listen for messages on Telegram.

### 5. Usage
- Start a chat with your bot on Telegram.
- Send a message like:
   ```
   /menu Rosół, Schabowy, Sernik
   ```
- The bot will reply with a PNG image of the menu.

### 6. Deployment (Google Cloud)
- Create a VM instance (Ubuntu recommended).
- Upload your project files (zip and unzip, or upload individually).
- Follow installation and running steps above.
- Use `tmux` or `screen` to keep the bot running 24/7.

### 7. Updating the Bot
- Upload changed files to the VM (overwrite old files).
- Restart the bot process.

## Customizing Layout
- To change margins, content area, or typography, edit the `LAYOUT` dictionary in `generate_menu.py`.
- To move the menu content closer to the top, lower the values for `"top_band"`, `"y_top"`, and `"first_baseline_y_top"` in `LAYOUT`.
- To center the menu vertically, set `"vertical_align": "middle"` in `LAYOUT`. The menu will be centered within the content area, respecting the top margin (`y_top`).
- To start the menu at a specific position from the top, set `"vertical_align": "top"` and adjust `"first_baseline_y_top"`.

## Troubleshooting
- **Font errors:** Use a TTF font with TrueType outlines.
- **Polish characters not showing:** Ensure the font supports Polish glyphs and is registered correctly.
- **Excel errors:** Make sure your Excel file has the correct columns: Category, Name, Description.
- **Content runs off the page:** Lower the top margin or add pagination logic if needed.

## License
This project is for educational and personal use. Please ensure you have the rights to use the font and images you provide.
