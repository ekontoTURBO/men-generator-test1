# Restaurant Menu Generator

This project generates a print-ready restaurant menu PDF from an Excel file, using a customizable layout and font. It is designed for Polish restaurants but can be adapted for others.

## Features
- Reads menu data from `menu_data.xlsx`
- Customizable layout and typography via the `LAYOUT` config in `generate_menu.py`
- Embeds a background image (`menu_background.png`)
- Uses a custom font (Argent.ttf) for all text
- Supports Polish characters (with a compatible TTF font)
- Telegram-style command interface for selecting menu dishes
- All text is centered and formatted according to print-safe rules
- Dishes are grouped by category, with category titles shown once above their dishes
- Top margin and content start position are easily adjustable
- Supports vertical centering of menu content (set `vertical_align` to `"middle"` in `LAYOUT`)
- If `vertical_align` is set to `"top"`, the menu starts at `first_baseline_y_top` (distance from top edge)

## Setup
1. **Install Python 3.10+**
2. **Install dependencies:**
   ```powershell
   pip install pandas reportlab
   ```
3. **Prepare your files:**
   - Place your menu data in `menu_data.xlsx` (columns: Category, Name, Description)
   - Place your background image as `menu_background.png`
   - Place your font file as `fonts/Argent.ttf` (must be a TrueType TTF font with Polish support)

## Usage
1. Open a terminal in the `restaurant_menu_project` directory.
2. Run the script:
   ```powershell
   python generate_menu.py
   ```
3. Follow the prompt. Type a command like:
   ```
   /menu Rosół, Schabowy, Sernik
   ```
   or any list of dish names separated by commas. The program will group dishes by category and display each category title once above its dishes.
4. The generated PDF will be saved as `menu_output.pdf`.

## Customizing Layout
- To change margins, content area, or typography, edit the `LAYOUT` dictionary in `generate_menu.py`.
- To move the menu content closer to the top, lower the values for `"top_band"`, `"y_top"`, and `"first_baseline_y_top"` in `LAYOUT`.
- To center the menu vertically, set `"vertical_align": "middle"` in `LAYOUT`. The menu will be centered within the content area, respecting the top margin (`y_top`).
- To start the menu at a specific position from the top, set `"vertical_align": "top"` and adjust `"first_baseline_y_top"`.
- Example:
  ```python
  "margins": {"L": 24, "R": 24, "B": 24, "top_band": 20},
  "content": {"x": 24, "y_top": 20, "w": 371.25, "h": 555.5},
  "spacing": {"first_baseline_y_top": 40, ...}
  "vertical_align": "middle"
  ```

## What is this project for?
This project helps restaurants quickly generate professional, print-ready menus from spreadsheet data, with full support for Polish language and custom branding.

## Troubleshooting
- **Font errors:** Use a TTF font with TrueType outlines.
- **Polish characters not showing:** Ensure the font supports Polish glyphs and is registered correctly.
- **Excel errors:** Make sure your Excel file has the correct columns: Category, Name, Description.
- **Content runs off the page:** Lower the top margin or add pagination logic if needed.

## License
This project is for educational and personal use. Please ensure you have the rights to use the font and images you provide.
