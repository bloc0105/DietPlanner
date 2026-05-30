MACRO_KEYS = ('kcal', 'protein', 'fat', 'carbs', 'fiber')


def per_serving(ingredient):
    """Return per-serving macro dict for one serving of an ingredient."""
    size = ingredient['serving_size'] or 100
    return {k: round((ingredient[k] or 0) * size / 100, 2) for k in MACRO_KEYS}


def recipe_totals(recipe_ingredients):
    """
    recipe_ingredients: list of dicts, each with ingredient columns + 'servings'.
    Returns combined macro totals for the whole recipe.
    """
    totals = {k: 0.0 for k in MACRO_KEYS}
    for ri in recipe_ingredients:
        ps = per_serving(ri)
        svgs = ri['servings'] or 1
        for k in MACRO_KEYS:
            totals[k] += ps[k] * svgs
    return {k: round(v, 2) for k, v in totals.items()}


def plan_day_totals(plan_rows):
    """
    plan_rows: list of dicts with recipe macro totals + 'servings' (of the recipe).
    Each dict must have pre-computed recipe-level MACRO_KEYS values.
    Returns combined macro totals for a day.
    """
    totals = {k: 0.0 for k in MACRO_KEYS}
    for row in plan_rows:
        svgs = row['servings'] or 1
        for k in MACRO_KEYS:
            totals[k] += (row[k] or 0) * svgs
    return {k: round(v, 2) for k, v in totals.items()}
