import sqlite3
import os
from datetime import date, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "meal_planner.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS family_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            preferences TEXT DEFAULT '',
            allergies TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT DEFAULT '',
            servings INTEGER DEFAULT 4,
            prep_time INTEGER DEFAULT 0,
            cook_time INTEGER DEFAULT 0,
            instructions TEXT DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS recipe_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT DEFAULT '',
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS meal_plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            meal_type TEXT NOT NULL CHECK(meal_type IN ('breakfast', 'lunch', 'dinner', 'snack')),
            recipe_id INTEGER NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS inventory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity REAL NOT NULL DEFAULT 0,
            unit TEXT DEFAULT '',
            category TEXT DEFAULT 'other'
        );

        CREATE TABLE IF NOT EXISTS shopping_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity REAL NOT NULL DEFAULT 0,
            unit TEXT DEFAULT '',
            purchased INTEGER DEFAULT 0
        );
    """)
    conn.commit()
    conn.close()


# --- Family Members ---

def get_family_members():
    conn = get_db()
    members = conn.execute("SELECT * FROM family_members ORDER BY name").fetchall()
    conn.close()
    return members


def add_family_member(name, preferences="", allergies=""):
    conn = get_db()
    conn.execute(
        "INSERT INTO family_members (name, preferences, allergies) VALUES (?, ?, ?)",
        (name, preferences, allergies),
    )
    conn.commit()
    conn.close()


def update_family_member(member_id, name, preferences, allergies):
    conn = get_db()
    conn.execute(
        "UPDATE family_members SET name=?, preferences=?, allergies=? WHERE id=?",
        (name, preferences, allergies, member_id),
    )
    conn.commit()
    conn.close()


def delete_family_member(member_id):
    conn = get_db()
    conn.execute("DELETE FROM family_members WHERE id=?", (member_id,))
    conn.commit()
    conn.close()


# --- Recipes ---

def get_recipes():
    conn = get_db()
    recipes = conn.execute("SELECT * FROM recipes ORDER BY name").fetchall()
    conn.close()
    return recipes


def get_recipe(recipe_id):
    conn = get_db()
    recipe = conn.execute("SELECT * FROM recipes WHERE id=?", (recipe_id,)).fetchone()
    ingredients = conn.execute(
        "SELECT * FROM recipe_ingredients WHERE recipe_id=? ORDER BY name",
        (recipe_id,),
    ).fetchall()
    conn.close()
    return recipe, ingredients


def add_recipe(name, description, servings, prep_time, cook_time, instructions, ingredients):
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO recipes (name, description, servings, prep_time, cook_time, instructions) VALUES (?, ?, ?, ?, ?, ?)",
        (name, description, servings, prep_time, cook_time, instructions),
    )
    recipe_id = cur.lastrowid
    for ing in ingredients:
        if ing["name"].strip():
            conn.execute(
                "INSERT INTO recipe_ingredients (recipe_id, name, quantity, unit) VALUES (?, ?, ?, ?)",
                (recipe_id, ing["name"], ing["quantity"], ing["unit"]),
            )
    conn.commit()
    conn.close()
    return recipe_id


def update_recipe(recipe_id, name, description, servings, prep_time, cook_time, instructions, ingredients):
    conn = get_db()
    conn.execute(
        "UPDATE recipes SET name=?, description=?, servings=?, prep_time=?, cook_time=?, instructions=? WHERE id=?",
        (name, description, servings, prep_time, cook_time, instructions, recipe_id),
    )
    conn.execute("DELETE FROM recipe_ingredients WHERE recipe_id=?", (recipe_id,))
    for ing in ingredients:
        if ing["name"].strip():
            conn.execute(
                "INSERT INTO recipe_ingredients (recipe_id, name, quantity, unit) VALUES (?, ?, ?, ?)",
                (recipe_id, ing["name"], ing["quantity"], ing["unit"]),
            )
    conn.commit()
    conn.close()


def delete_recipe(recipe_id):
    conn = get_db()
    conn.execute("DELETE FROM recipes WHERE id=?", (recipe_id,))
    conn.commit()
    conn.close()


# --- Meal Plan ---

def get_meal_plan(start_date, days=7):
    conn = get_db()
    end_date = start_date + timedelta(days=days - 1)
    rows = conn.execute(
        """SELECT mp.id, mp.date, mp.meal_type, mp.recipe_id, r.name as recipe_name
           FROM meal_plan mp JOIN recipes r ON mp.recipe_id = r.id
           WHERE mp.date BETWEEN ? AND ?
           ORDER BY mp.date, mp.meal_type""",
        (start_date.isoformat(), end_date.isoformat()),
    ).fetchall()
    conn.close()

    plan = {}
    for i in range(days):
        d = (start_date + timedelta(days=i)).isoformat()
        plan[d] = {"breakfast": [], "lunch": [], "dinner": [], "snack": []}
    for row in rows:
        if row["date"] in plan:
            plan[row["date"]][row["meal_type"]].append(dict(row))
    return plan


def add_meal(meal_date, meal_type, recipe_id):
    conn = get_db()
    conn.execute(
        "INSERT INTO meal_plan (date, meal_type, recipe_id) VALUES (?, ?, ?)",
        (meal_date, meal_type, recipe_id),
    )
    conn.commit()
    conn.close()


def delete_meal(meal_id):
    conn = get_db()
    conn.execute("DELETE FROM meal_plan WHERE id=?", (meal_id,))
    conn.commit()
    conn.close()


# --- Inventory ---

def get_inventory():
    conn = get_db()
    items = conn.execute("SELECT * FROM inventory ORDER BY category, name").fetchall()
    conn.close()
    return items


def add_inventory_item(name, quantity, unit, category):
    conn = get_db()
    conn.execute(
        "INSERT INTO inventory (name, quantity, unit, category) VALUES (?, ?, ?, ?)",
        (name, quantity, unit, category),
    )
    conn.commit()
    conn.close()


def update_inventory_item(item_id, name, quantity, unit, category):
    conn = get_db()
    conn.execute(
        "UPDATE inventory SET name=?, quantity=?, unit=?, category=? WHERE id=?",
        (name, quantity, unit, category, item_id),
    )
    conn.commit()
    conn.close()


def delete_inventory_item(item_id):
    conn = get_db()
    conn.execute("DELETE FROM inventory WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


# --- Shopping List ---

def get_shopping_list():
    conn = get_db()
    items = conn.execute("SELECT * FROM shopping_list ORDER BY purchased, name").fetchall()
    conn.close()
    return items


def add_shopping_item(name, quantity, unit):
    conn = get_db()
    conn.execute(
        "INSERT INTO shopping_list (name, quantity, unit) VALUES (?, ?, ?)",
        (name, quantity, unit),
    )
    conn.commit()
    conn.close()


def toggle_shopping_item(item_id):
    conn = get_db()
    conn.execute(
        "UPDATE shopping_list SET purchased = NOT purchased WHERE id=?",
        (item_id,),
    )
    conn.commit()
    conn.close()


def delete_shopping_item(item_id):
    conn = get_db()
    conn.execute("DELETE FROM shopping_list WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


def clear_purchased():
    conn = get_db()
    conn.execute("DELETE FROM shopping_list WHERE purchased = 1")
    conn.commit()
    conn.close()


def generate_shopping_list_from_plan(start_date, days=7):
    """Generate shopping list from meal plan, subtracting inventory."""
    conn = get_db()
    end_date = start_date + timedelta(days=days - 1)

    needed = conn.execute(
        """SELECT ri.name, SUM(ri.quantity) as total_qty, ri.unit
           FROM meal_plan mp
           JOIN recipe_ingredients ri ON mp.recipe_id = ri.recipe_id
           WHERE mp.date BETWEEN ? AND ?
           GROUP BY LOWER(ri.name), ri.unit""",
        (start_date.isoformat(), end_date.isoformat()),
    ).fetchall()

    inventory = {row["name"].lower(): row for row in conn.execute("SELECT * FROM inventory").fetchall()}

    for item in needed:
        inv = inventory.get(item["name"].lower())
        qty_needed = item["total_qty"]
        if inv:
            qty_needed = max(0, qty_needed - inv["quantity"])
        if qty_needed > 0:
            existing = conn.execute(
                "SELECT id, quantity FROM shopping_list WHERE LOWER(name) = LOWER(?) AND unit = ?",
                (item["name"], item["unit"]),
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE shopping_list SET quantity = ? WHERE id = ?",
                    (qty_needed, existing["id"]),
                )
            else:
                conn.execute(
                    "INSERT INTO shopping_list (name, quantity, unit) VALUES (?, ?, ?)",
                    (item["name"], qty_needed, item["unit"]),
                )
    conn.commit()
    conn.close()
