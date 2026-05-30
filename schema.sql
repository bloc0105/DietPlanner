CREATE TABLE IF NOT EXISTS ingredients (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT    NOT NULL,
    upc          TEXT,
    serving_size REAL,
    serving_unit TEXT,
    kcal         REAL,
    protein      REAL,
    fat          REAL,
    carbs        REAL,
    fiber        REAL
);

CREATE TABLE IF NOT EXISTS recipes (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recipe_ingredients (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    recipe_id     INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    ingredient_id INTEGER NOT NULL REFERENCES ingredients(id),
    servings      REAL    NOT NULL
);

CREATE TABLE IF NOT EXISTS plan (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    day       INTEGER NOT NULL CHECK(day BETWEEN 1 AND 14),
    recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    servings  REAL    NOT NULL
);
