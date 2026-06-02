import os
from flask import Flask, redirect, url_for, render_template, request, jsonify, abort
from dotenv import load_dotenv

load_dotenv()

from db import get_db, init_db
from usda import lookup_fdc_id
from nutrition import recipe_totals, plan_day_totals, MACRO_KEYS

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret')

init_db(app)


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------

@app.route('/')
def index():
    return redirect(url_for('plan_view'))


# ---------------------------------------------------------------------------
# Ingredients
# ---------------------------------------------------------------------------

@app.route('/ingredients')
def ingredients_index():
    db = get_db()
    rows = db.execute('SELECT * FROM ingredients ORDER BY name').fetchall()
    return render_template('ingredients/index.html', ingredients=rows)


@app.route('/ingredients/new')
def ingredients_new():
    return render_template('ingredients/new.html', prefill=None, error=None)


@app.route('/ingredients/lookup')
def ingredients_lookup():
    fdc_id = request.args.get('fdc_id', '').strip()
    if not fdc_id:
        return jsonify({'error': 'No FDC ID provided'}), 400
    try:
        data = lookup_fdc_id(fdc_id)
    except Exception as e:
        return jsonify({'error': str(e)}), 502
    if data is None:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(data)


@app.route('/ingredients', methods=['POST'])
def ingredients_save():
    db = get_db()
    name = request.form.get('name', '').strip()
    if not name:
        return render_template('ingredients/new.html', prefill=request.form, error='Name is required')
    db.execute(
        '''INSERT INTO ingredients (name, upc, serving_size, serving_unit, kcal, protein, fat, carbs, fiber)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (
            name,
            request.form.get('upc') or None,
            _float(request.form.get('serving_size')),
            request.form.get('serving_unit') or 'g',
            _float(request.form.get('kcal')),
            _float(request.form.get('protein')),
            _float(request.form.get('fat')),
            _float(request.form.get('carbs')),
            _float(request.form.get('fiber')),
        ),
    )
    db.commit()
    return redirect(url_for('ingredients_index'))


@app.route('/ingredients/<int:id>/edit', methods=['GET', 'POST'])
def ingredients_edit(id):
    db = get_db()
    ingredient = db.execute('SELECT * FROM ingredients WHERE id = ?', (id,)).fetchone()
    if ingredient is None:
        abort(404)
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            return render_template('ingredients/edit.html', ingredient=ingredient, error='Name is required')
        db.execute(
            '''UPDATE ingredients SET name=?, upc=?, serving_size=?, serving_unit=?,
               kcal=?, protein=?, fat=?, carbs=?, fiber=? WHERE id=?''',
            (
                name,
                request.form.get('upc') or None,
                _float(request.form.get('serving_size')),
                request.form.get('serving_unit') or 'g',
                _float(request.form.get('kcal')),
                _float(request.form.get('protein')),
                _float(request.form.get('fat')),
                _float(request.form.get('carbs')),
                _float(request.form.get('fiber')),
                id,
            ),
        )
        db.commit()
        return redirect(url_for('ingredients_index'))
    return render_template('ingredients/edit.html', ingredient=ingredient, error=None)


# ---------------------------------------------------------------------------
# Recipes
# ---------------------------------------------------------------------------

@app.route('/recipes')
def recipes_index():
    db = get_db()
    recipes = db.execute('SELECT * FROM recipes ORDER BY name').fetchall()
    return render_template('recipes/index.html', recipes=recipes)


@app.route('/recipes/new', methods=['GET', 'POST'])
def recipes_new():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        if not name:
            return render_template('recipes/new.html', error='Name is required')
        db = get_db()
        cur = db.execute('INSERT INTO recipes (name) VALUES (?)', (name,))
        db.commit()
        return redirect(url_for('recipes_edit', id=cur.lastrowid))
    return render_template('recipes/new.html', error=None)


@app.route('/recipes/<int:id>/edit', methods=['GET', 'POST'])
def recipes_edit(id):
    db = get_db()
    recipe = db.execute('SELECT * FROM recipes WHERE id = ?', (id,)).fetchone()
    if recipe is None:
        abort(404)

    if request.method == 'POST':
        new_name = request.form.get('name', '').strip()
        if new_name:
            db.execute('UPDATE recipes SET name=? WHERE id=?', (new_name, id))
            db.commit()

    ri_rows = db.execute(
        '''SELECT ri.id, ri.servings,
                  i.id as ingredient_id, i.name, i.serving_size, i.serving_unit,
                  i.kcal, i.protein, i.fat, i.carbs, i.fiber
           FROM recipe_ingredients ri
           JOIN ingredients i ON i.id = ri.ingredient_id
           WHERE ri.recipe_id = ?
           ORDER BY i.name''',
        (id,),
    ).fetchall()

    all_ingredients = db.execute('SELECT * FROM ingredients ORDER BY name').fetchall()
    totals = recipe_totals([dict(r) for r in ri_rows])

    return render_template(
        'recipes/edit.html',
        recipe=recipe,
        ri_rows=ri_rows,
        all_ingredients=all_ingredients,
        totals=totals,
        macro_keys=MACRO_KEYS,
        error=None,
    )


@app.route('/recipes/<int:id>/ingredients', methods=['POST'])
def recipe_add_ingredient(id):
    db = get_db()
    ingredient_id = request.form.get('ingredient_id')
    servings = _float(request.form.get('servings')) or 1.0
    if not ingredient_id:
        return redirect(url_for('recipes_edit', id=id))
    db.execute(
        'INSERT INTO recipe_ingredients (recipe_id, ingredient_id, servings) VALUES (?, ?, ?)',
        (id, ingredient_id, servings),
    )
    db.commit()
    return redirect(url_for('recipes_edit', id=id))


@app.route('/recipe_ingredients/<int:id>/delete', methods=['POST'])
def recipe_ingredient_delete(id):
    db = get_db()
    ri = db.execute('SELECT recipe_id FROM recipe_ingredients WHERE id = ?', (id,)).fetchone()
    if ri is None:
        abort(404)
    recipe_id = ri['recipe_id']
    db.execute('DELETE FROM recipe_ingredients WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('recipes_edit', id=recipe_id))


@app.route('/recipe_ingredients/<int:id>/servings', methods=['POST'])
def recipe_ingredient_servings(id):
    db = get_db()
    ri = db.execute('SELECT recipe_id FROM recipe_ingredients WHERE id = ?', (id,)).fetchone()
    if ri is None:
        abort(404)
    recipe_id = ri['recipe_id']
    servings = _float(request.form.get('servings')) or 1.0
    db.execute('UPDATE recipe_ingredients SET servings=? WHERE id=?', (servings, id))
    db.commit()
    return redirect(url_for('recipes_edit', id=recipe_id))


# ---------------------------------------------------------------------------
# Plan
# ---------------------------------------------------------------------------

def _build_plan_data(db):
    """Return plan rows grouped by day (1-14) with per-recipe totals."""
    plan_rows = db.execute(
        '''SELECT p.id, p.day, p.servings as plan_servings, r.id as recipe_id, r.name as recipe_name
           FROM plan p
           JOIN recipes r ON r.id = p.recipe_id
           ORDER BY p.day, r.name''',
    ).fetchall()

    days = {d: [] for d in range(1, 15)}
    for row in plan_rows:
        ri_rows = db.execute(
            '''SELECT ri.servings, i.serving_size, i.kcal, i.protein, i.fat, i.carbs, i.fiber
               FROM recipe_ingredients ri JOIN ingredients i ON i.id = ri.ingredient_id
               WHERE ri.recipe_id = ?''',
            (row['recipe_id'],),
        ).fetchall()
        rt = recipe_totals([dict(r) for r in ri_rows])
        days[row['day']].append({
            'plan_id': row['id'],
            'recipe_id': row['recipe_id'],
            'recipe_name': row['recipe_name'],
            'plan_servings': row['plan_servings'],
            'recipe_totals': rt,
        })

    day_totals = {}
    for d, entries in days.items():
        rows_for_total = [
            {**e['recipe_totals'], 'servings': e['plan_servings']}
            for e in entries
        ]
        day_totals[d] = plan_day_totals(rows_for_total)

    return days, day_totals


@app.route('/plan')
def plan_view():
    db = get_db()
    days, day_totals = _build_plan_data(db)
    all_recipes = db.execute('SELECT * FROM recipes ORDER BY name').fetchall()
    return render_template(
        'plan/index.html',
        days=days,
        day_totals=day_totals,
        all_recipes=all_recipes,
        macro_keys=MACRO_KEYS,
    )


@app.route('/plan', methods=['POST'])
def plan_assign():
    db = get_db()
    day = int(request.form.get('day', 0))
    recipe_id = request.form.get('recipe_id')
    servings = _float(request.form.get('servings')) or 1.0
    if not (1 <= day <= 14) or not recipe_id:
        return redirect(url_for('plan_view'))
    db.execute(
        'INSERT INTO plan (day, recipe_id, servings) VALUES (?, ?, ?)',
        (day, recipe_id, servings),
    )
    db.commit()
    return redirect(url_for('plan_view'))


@app.route('/plan/<int:id>/delete', methods=['POST'])
def plan_delete(id):
    db = get_db()
    db.execute('DELETE FROM plan WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('plan_view'))


@app.route('/plan/clear', methods=['POST'])
def plan_clear():
    db = get_db()
    db.execute('DELETE FROM plan')
    db.commit()
    return redirect(url_for('plan_view'))


@app.route('/plan/print')
def plan_print():
    db = get_db()
    days, day_totals = _build_plan_data(db)
    return render_template('print.html', days=days, day_totals=day_totals, macro_keys=MACRO_KEYS)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _float(val):
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


if __name__ == '__main__':
    app.run(debug=True)
