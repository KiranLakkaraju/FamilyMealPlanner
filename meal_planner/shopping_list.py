"""Shopping list generation from a meal plan and current inventory."""

from typing import Dict, List, Tuple

from meal_planner.inventory import InventoryManager
from meal_planner.models import Ingredient, MealPlan, Unit


class ShoppingListItem:
    def __init__(self, name: str, quantity: float, unit: Unit):
        self.name = name
        self.quantity = quantity
        self.unit = unit

    def __repr__(self):
        return f"ShoppingListItem({self.name!r}, {self.quantity}, {self.unit})"

    def __eq__(self, other):
        if not isinstance(other, ShoppingListItem):
            return NotImplemented
        return self.name == other.name and self.quantity == other.quantity and self.unit == other.unit


def generate_shopping_list(
    meal_plan: MealPlan,
    inventory: InventoryManager,
) -> List[ShoppingListItem]:
    """
    Generate a shopping list for a meal plan, subtracting what is already in inventory.

    For each ingredient required across all planned meals, calculates the total
    needed and subtracts available inventory, returning only items that still
    need to be purchased.
    """
    needed: Dict[Tuple[str, Unit], float] = {}

    for planned_meal in meal_plan.meals:
        recipe = planned_meal.recipe
        scale_factor = planned_meal.servings / recipe.servings
        for ingredient in recipe.ingredients:
            key = (ingredient.name.strip().lower(), ingredient.unit)
            required = ingredient.quantity * scale_factor
            needed[key] = needed.get(key, 0.0) + required

    shopping_list = []
    for (name, unit), total_needed in needed.items():
        inventory_item = inventory.get_item(name)
        if inventory_item is not None and inventory_item.unit == unit:
            shortfall = total_needed - inventory_item.quantity
        else:
            shortfall = total_needed

        if shortfall > 0:
            shopping_list.append(ShoppingListItem(name, shortfall, unit))

    return sorted(shopping_list, key=lambda x: x.name)


def merge_shopping_lists(
    *lists: List[ShoppingListItem],
) -> List[ShoppingListItem]:
    """Combine multiple shopping lists, summing quantities for matching items."""
    merged: Dict[Tuple[str, Unit], float] = {}
    for shopping_list in lists:
        for item in shopping_list:
            key = (item.name, item.unit)
            merged[key] = merged.get(key, 0.0) + item.quantity
    return sorted(
        [ShoppingListItem(name, qty, unit) for (name, unit), qty in merged.items()],
        key=lambda x: x.name,
    )
