from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date, timedelta, datetime
import models

app = Flask(__name__)
app.secret_key = "family-meal-planner-secret-key"


@app.before_request
def ensure_db():
    models.init_db()


# --- Home / Meal Plan ---

@app.route("/")
def index():
    week_offset = int(request.args.get("week", 0))
    today = date.today()
    start = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    plan = models.get_meal_plan(start, 7)
    recipes = models.get_recipes()
    days = []
    for i in range(7):
        d = start + timedelta(days=i)
        days.append({
            "date": d.isoformat(),
            "label": d.strftime("%A, %b %d"),
            "is_today": d == today,
        })
    return render_template(
        "index.html",
        plan=plan,
        days=days,
        recipes=recipes,
        week_offset=week_offset,
        week_label=f"{start.strftime('%b %d')} - {(start + timedelta(days=6)).strftime('%b %d, %Y')}",
    )


@app.route("/meal/add", methods=["POST"])
def add_meal():
    models.add_meal(request.form["date"], request.form["meal_type"], int(request.form["recipe_id"]))
    flash("Meal added!", "success")
    return redirect(url_for("index", week=request.form.get("week", 0)))


@app.route("/meal/delete/<int:meal_id>")
def delete_meal(meal_id):
    models.delete_meal(meal_id)
    flash("Meal removed.", "info")
    return redirect(request.referrer or url_for("index"))


# --- Recipes ---

@app.route("/recipes")
def recipes():
    return render_template("recipes.html", recipes=models.get_recipes())


@app.route("/recipes/new", methods=["GET", "POST"])
def new_recipe():
    if request.method == "POST":
        ingredients = _parse_ingredients(request.form)
        models.add_recipe(
            request.form["name"],
            request.form.get("description", ""),
            int(request.form.get("servings", 4)),
            int(request.form.get("prep_time", 0)),
            int(request.form.get("cook_time", 0)),
            request.form.get("instructions", ""),
            ingredients,
        )
        flash("Recipe created!", "success")
        return redirect(url_for("recipes"))
    return render_template("recipe_form.html", recipe=None, ingredients=[])


@app.route("/recipes/<int:recipe_id>")
def view_recipe(recipe_id):
    recipe, ingredients = models.get_recipe(recipe_id)
    if not recipe:
        flash("Recipe not found.", "danger")
        return redirect(url_for("recipes"))
    return render_template("recipe_view.html", recipe=recipe, ingredients=ingredients)


@app.route("/recipes/<int:recipe_id>/edit", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    if request.method == "POST":
        ingredients = _parse_ingredients(request.form)
        models.update_recipe(
            recipe_id,
            request.form["name"],
            request.form.get("description", ""),
            int(request.form.get("servings", 4)),
            int(request.form.get("prep_time", 0)),
            int(request.form.get("cook_time", 0)),
            request.form.get("instructions", ""),
            ingredients,
        )
        flash("Recipe updated!", "success")
        return redirect(url_for("view_recipe", recipe_id=recipe_id))
    recipe, ingredients = models.get_recipe(recipe_id)
    return render_template("recipe_form.html", recipe=recipe, ingredients=ingredients)


@app.route("/recipes/<int:recipe_id>/delete")
def delete_recipe(recipe_id):
    models.delete_recipe(recipe_id)
    flash("Recipe deleted.", "info")
    return redirect(url_for("recipes"))


def _parse_ingredients(form):
    ingredients = []
    i = 0
    while f"ing_name_{i}" in form:
        name = form.get(f"ing_name_{i}", "").strip()
        if name:
            ingredients.append({
                "name": name,
                "quantity": float(form.get(f"ing_qty_{i}", 0) or 0),
                "unit": form.get(f"ing_unit_{i}", ""),
            })
        i += 1
    return ingredients


# --- Family Members ---

@app.route("/family")
def family():
    return render_template("family.html", members=models.get_family_members())


@app.route("/family/add", methods=["POST"])
def add_family_member():
    models.add_family_member(
        request.form["name"],
        request.form.get("preferences", ""),
        request.form.get("allergies", ""),
    )
    flash("Family member added!", "success")
    return redirect(url_for("family"))


@app.route("/family/<int:member_id>/edit", methods=["POST"])
def edit_family_member(member_id):
    models.update_family_member(
        member_id,
        request.form["name"],
        request.form.get("preferences", ""),
        request.form.get("allergies", ""),
    )
    flash("Family member updated!", "success")
    return redirect(url_for("family"))


@app.route("/family/<int:member_id>/delete")
def delete_family_member(member_id):
    models.delete_family_member(member_id)
    flash("Family member removed.", "info")
    return redirect(url_for("family"))


# --- Inventory ---

@app.route("/inventory")
def inventory():
    return render_template("inventory.html", items=models.get_inventory())


@app.route("/inventory/add", methods=["POST"])
def add_inventory_item():
    models.add_inventory_item(
        request.form["name"],
        float(request.form.get("quantity", 0) or 0),
        request.form.get("unit", ""),
        request.form.get("category", "other"),
    )
    flash("Item added to inventory!", "success")
    return redirect(url_for("inventory"))


@app.route("/inventory/<int:item_id>/edit", methods=["POST"])
def edit_inventory_item(item_id):
    models.update_inventory_item(
        item_id,
        request.form["name"],
        float(request.form.get("quantity", 0) or 0),
        request.form.get("unit", ""),
        request.form.get("category", "other"),
    )
    flash("Inventory updated!", "success")
    return redirect(url_for("inventory"))


@app.route("/inventory/<int:item_id>/delete")
def delete_inventory_item(item_id):
    models.delete_inventory_item(item_id)
    flash("Item removed from inventory.", "info")
    return redirect(url_for("inventory"))


# --- Shopping List ---

@app.route("/shopping")
def shopping():
    return render_template("shopping.html", items=models.get_shopping_list())


@app.route("/shopping/add", methods=["POST"])
def add_shopping_item():
    models.add_shopping_item(
        request.form["name"],
        float(request.form.get("quantity", 0) or 0),
        request.form.get("unit", ""),
    )
    flash("Item added to shopping list!", "success")
    return redirect(url_for("shopping"))


@app.route("/shopping/<int:item_id>/toggle")
def toggle_shopping_item(item_id):
    models.toggle_shopping_item(item_id)
    return redirect(url_for("shopping"))


@app.route("/shopping/<int:item_id>/delete")
def delete_shopping_item(item_id):
    models.delete_shopping_item(item_id)
    flash("Item removed.", "info")
    return redirect(url_for("shopping"))


@app.route("/shopping/clear")
def clear_purchased():
    models.clear_purchased()
    flash("Purchased items cleared.", "info")
    return redirect(url_for("shopping"))


@app.route("/shopping/generate", methods=["POST"])
def generate_shopping():
    week_offset = int(request.form.get("week", 0))
    today = date.today()
    start = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    models.generate_shopping_list_from_plan(start, 7)
    flash("Shopping list generated from meal plan!", "success")
    return redirect(url_for("shopping"))


if __name__ == "__main__":
    models.init_db()
    app.run(debug=True, port=5000)
