# Diet Planner

A local meal planning app built with Python/Flask and SQLite. Look up foods from the USDA database, build recipes, assign them to a 14-day plan, and print it out.

## Requirements

- Python 3.8+
- A free USDA FoodData Central API key — get one at https://fdc.nal.usda.gov/api-guide.html

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create your .env file
cp .env.example .env
```

Edit `.env` and fill in your keys:

```
USDA_API_KEY=your_key_here
FLASK_SECRET_KEY=any-random-string
```

## Running

```bash
python3 app.py
```

Then open http://localhost:5000 in your browser. The database (`diet.db`) is created automatically on first run.

## Usage

### 1. Add ingredients

Go to **Ingredients → Add Ingredient**.

To auto-fill nutrition data from the USDA database:
1. Visit https://fdc.nal.usda.gov and search for a food
2. Click a result — the FDC ID is the number in the URL (e.g. `https://fdc.nal.usda.gov/food-details/171477/...` → ID is `171477`)
3. Paste the ID into the lookup box and click **Look up**
4. Review the pre-filled values and click **Save Ingredient**

You can also fill in nutrition values manually if a food isn't in the USDA database. All values are stored per 100g/ml and normalized automatically from the USDA serving size.

### 2. Build recipes

Go to **Recipes → New Recipe**, give it a name, then add ingredients and set servings for each. Macro totals update on the page after each change.

### 3. Plan your two weeks

Go to **Plan**, pick a day (1–14), choose a recipe, set servings, and click **Add**. Daily macro totals are shown at the bottom of each day card.

### 4. Print

Click **Print view** (opens in a new tab) for a clean landscape table — 14 columns, one per day, with daily macro totals at the bottom. Use your browser's print dialog to send it to a printer or save as PDF.

## Project structure

```
app.py          # Flask routes
db.py           # SQLite connection and init
usda.py         # USDA FoodData Central API client
nutrition.py    # Server-side macro math
schema.sql      # Database schema
templates/      # Jinja2 templates
diet.db         # SQLite database (created on first run, gitignored)
```
