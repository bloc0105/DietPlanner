Here's the brief:

---

**Diet Planner App — Project Brief**

**Stack**
- Python / Flask
- SQLite
- Jinja2 templates
- CSS print styles
- USDA FoodData Central API

**USDA API**
- Base URL: `https://api.nal.usda.gov/fdc/v1`
- Key: stored in a `.env` file, never hardcoded
- Lookup by UPC: `/foods/search?query=<upc>&api_key=<key>`
- We want `labelNutrients` from the response: calories, protein, fat, carbohydrates, fiber
- Also store: `servingSize`, `servingSizeUnit`, `description`, `gtinUpc`
- Normalize all nutrition to per 100g/ml for storage

**Database — three tables**

`ingredients`
- id, name, upc, serving_size, serving_unit, kcal, protein, fat, carbs, fiber

`recipes`
- id, name
- recipe_ingredients: id, recipe_id, ingredient_id, servings

`plan`
- id, day (1-14), recipe_id, servings

**Core app workflow**
1. User enters a UPC → app calls USDA API → nutrition data auto-fills → user saves to ingredients
2. User creates a recipe → picks ingredients from dropdown → enters servings for each → app shows live macro totals
3. User builds two week plan → assigns recipes to days → app shows daily macro totals
4. User prints → clean 8.5x11 view, 14 columns one per day, portions listed per day, daily macro totals at bottom

**Key behaviour**
- All nutrition math happens server side in Python
- Recipes store servings per ingredient, not absolute weights
- Plan stores servings of a recipe, allowing fractional portions
- Print view is a separate clean Jinja2 template with CSS print styles, no navigation, no UI chrome
- App runs locally, no authentication needed

**What a typical session looks like**
- User looks up a few ingredients by UPC
- Builds or tweaks a recipe, nudging servings until macros look right
- Assigns recipes to days across the two week plan
- Prints the plan to stick on the wall

---

That's everything Claude Code needs to get started. When you fire it up just paste that in and tell it to start with the database schema and Flask app structure first before touching any frontend.