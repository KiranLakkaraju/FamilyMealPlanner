"""Populate the database with sample recipes and family members."""
import models
from datetime import date, timedelta


def seed():
    models.init_db()

    # Family members
    models.add_family_member("Mom", "Mediterranean, healthy options", "")
    models.add_family_member("Dad", "Grilled food, hearty meals", "")
    models.add_family_member("Emma", "Pasta, mild flavors", "Peanuts")
    models.add_family_member("Jack", "Pizza, tacos", "")

    # Recipes
    models.add_recipe(
        "Spaghetti Bolognese",
        "Classic Italian meat sauce with spaghetti",
        4, 15, 30,
        "1. Cook spaghetti according to package directions.\n2. Brown ground beef in a large skillet.\n3. Add onion, garlic, and cook until soft.\n4. Stir in crushed tomatoes, tomato paste, and Italian seasoning.\n5. Simmer for 20 minutes.\n6. Serve sauce over spaghetti.",
        [
            {"name": "Spaghetti", "quantity": 1, "unit": "lb"},
            {"name": "Ground beef", "quantity": 1, "unit": "lb"},
            {"name": "Onion", "quantity": 1, "unit": ""},
            {"name": "Garlic", "quantity": 3, "unit": "cloves"},
            {"name": "Crushed tomatoes", "quantity": 28, "unit": "oz"},
            {"name": "Tomato paste", "quantity": 2, "unit": "tbsp"},
        ],
    )

    models.add_recipe(
        "Chicken Stir Fry",
        "Quick and healthy chicken with vegetables",
        4, 15, 15,
        "1. Cut chicken into strips and season.\n2. Cook chicken in a hot wok with oil.\n3. Remove chicken and stir fry vegetables.\n4. Add sauce (soy sauce, ginger, garlic).\n5. Return chicken to wok and toss together.\n6. Serve over rice.",
        [
            {"name": "Chicken breast", "quantity": 1.5, "unit": "lbs"},
            {"name": "Broccoli", "quantity": 2, "unit": "cups"},
            {"name": "Bell pepper", "quantity": 2, "unit": ""},
            {"name": "Soy sauce", "quantity": 3, "unit": "tbsp"},
            {"name": "Rice", "quantity": 2, "unit": "cups"},
            {"name": "Garlic", "quantity": 2, "unit": "cloves"},
        ],
    )

    models.add_recipe(
        "Pancakes",
        "Fluffy breakfast pancakes",
        4, 5, 15,
        "1. Mix flour, sugar, baking powder, and salt.\n2. Whisk milk, egg, and melted butter.\n3. Combine wet and dry ingredients.\n4. Cook on a griddle until bubbles form, then flip.\n5. Serve with maple syrup and fruit.",
        [
            {"name": "Flour", "quantity": 1.5, "unit": "cups"},
            {"name": "Milk", "quantity": 1.25, "unit": "cups"},
            {"name": "Eggs", "quantity": 1, "unit": ""},
            {"name": "Butter", "quantity": 3, "unit": "tbsp"},
            {"name": "Sugar", "quantity": 2, "unit": "tbsp"},
            {"name": "Baking powder", "quantity": 2, "unit": "tsp"},
        ],
    )

    models.add_recipe(
        "Grilled Cheese & Tomato Soup",
        "Comfort food classic",
        4, 10, 20,
        "1. Butter bread slices on one side.\n2. Place cheese between bread slices.\n3. Grill in a pan until golden on both sides.\n4. Heat tomato soup in a pot.\n5. Serve together.",
        [
            {"name": "Bread", "quantity": 8, "unit": "slices"},
            {"name": "Cheddar cheese", "quantity": 8, "unit": "slices"},
            {"name": "Butter", "quantity": 4, "unit": "tbsp"},
            {"name": "Tomato soup", "quantity": 2, "unit": "cans"},
        ],
    )

    models.add_recipe(
        "Tacos",
        "Seasoned beef tacos with all the fixings",
        4, 15, 15,
        "1. Brown ground beef and drain fat.\n2. Add taco seasoning and water, simmer.\n3. Warm taco shells.\n4. Set up toppings: lettuce, tomato, cheese, sour cream.\n5. Assemble and serve.",
        [
            {"name": "Ground beef", "quantity": 1, "unit": "lb"},
            {"name": "Taco shells", "quantity": 12, "unit": ""},
            {"name": "Lettuce", "quantity": 2, "unit": "cups"},
            {"name": "Tomato", "quantity": 2, "unit": ""},
            {"name": "Cheddar cheese", "quantity": 1, "unit": "cup"},
            {"name": "Sour cream", "quantity": 0.5, "unit": "cup"},
        ],
    )

    # Sample inventory
    models.add_inventory_item("Rice", 5, "lbs", "grains")
    models.add_inventory_item("Spaghetti", 2, "lbs", "grains")
    models.add_inventory_item("Olive oil", 1, "bottle", "condiments")
    models.add_inventory_item("Soy sauce", 1, "bottle", "condiments")
    models.add_inventory_item("Salt", 1, "container", "spices")
    models.add_inventory_item("Black pepper", 1, "container", "spices")
    models.add_inventory_item("Garlic", 1, "head", "produce")
    models.add_inventory_item("Butter", 1, "lb", "dairy")
    models.add_inventory_item("Milk", 1, "gallon", "dairy")
    models.add_inventory_item("Eggs", 12, "", "dairy")

    # Sample meal plan for this week
    today = date.today()
    monday = today - timedelta(days=today.weekday())

    models.add_meal(monday.isoformat(), "breakfast", 3)  # Pancakes
    models.add_meal(monday.isoformat(), "dinner", 1)     # Spaghetti
    models.add_meal((monday + timedelta(1)).isoformat(), "dinner", 2)  # Stir Fry
    models.add_meal((monday + timedelta(2)).isoformat(), "lunch", 4)   # Grilled Cheese
    models.add_meal((monday + timedelta(2)).isoformat(), "dinner", 5)  # Tacos
    models.add_meal((monday + timedelta(3)).isoformat(), "dinner", 1)  # Spaghetti
    models.add_meal((monday + timedelta(4)).isoformat(), "breakfast", 3)  # Pancakes
    models.add_meal((monday + timedelta(4)).isoformat(), "dinner", 2)  # Stir Fry
    models.add_meal((monday + timedelta(5)).isoformat(), "dinner", 5)  # Tacos
    models.add_meal((monday + timedelta(6)).isoformat(), "lunch", 4)   # Grilled Cheese

    print("Database seeded with sample data!")


if __name__ == "__main__":
    seed()
