"""Tests for shopping list generation."""

import pytest
from datetime import date

from meal_planner.inventory import InventoryManager
from meal_planner.models import Ingredient, InventoryItem, MealPlan, MealType, PlannedMeal, Recipe, Unit
from meal_planner.shopping_list import ShoppingListItem, generate_shopping_list, merge_shopping_lists


def make_pasta_recipe(servings=4):
    return Recipe(
        name="Pasta Bolognese",
        ingredients=[
            Ingredient("pasta", 400.0, Unit.GRAMS),
            Ingredient("tomato sauce", 500.0, Unit.MILLILITERS),
            Ingredient("ground beef", 300.0, Unit.GRAMS),
        ],
        servings=servings,
        meal_type=MealType.DINNER,
    )


def make_plan_with_one_meal(recipe, servings=4):
    plan = MealPlan("Test Plan", start_date=date(2026, 3, 4), end_date=date(2026, 3, 10))
    plan.add_meal(PlannedMeal(date(2026, 3, 5), MealType.DINNER, recipe, servings=servings))
    return plan


class TestGenerateShoppingList:
    def test_all_items_needed_when_inventory_empty(self):
        recipe = make_pasta_recipe(servings=4)
        plan = make_plan_with_one_meal(recipe, servings=4)
        inventory = InventoryManager()

        items = generate_shopping_list(plan, inventory)
        names = {i.name for i in items}
        assert "pasta" in names
        assert "tomato sauce" in names
        assert "ground beef" in names

    def test_existing_inventory_reduces_shopping_list(self):
        recipe = make_pasta_recipe(servings=4)
        plan = make_plan_with_one_meal(recipe, servings=4)

        inventory = InventoryManager()
        inventory.add_item(InventoryItem("pasta", 400.0, Unit.GRAMS))  # exactly enough

        items = generate_shopping_list(plan, inventory)
        names = {i.name for i in items}
        assert "pasta" not in names  # fully covered by inventory
        assert "tomato sauce" in names

    def test_partial_inventory_shows_shortfall(self):
        recipe = make_pasta_recipe(servings=4)
        plan = make_plan_with_one_meal(recipe, servings=4)

        inventory = InventoryManager()
        inventory.add_item(InventoryItem("pasta", 200.0, Unit.GRAMS))  # only half

        items = generate_shopping_list(plan, inventory)
        pasta_item = next(i for i in items if i.name == "pasta")
        assert pasta_item.quantity == pytest.approx(200.0)

    def test_scaled_servings_increases_quantity(self):
        recipe = make_pasta_recipe(servings=4)
        plan = make_plan_with_one_meal(recipe, servings=8)  # double the servings
        inventory = InventoryManager()

        items = generate_shopping_list(plan, inventory)
        pasta_item = next(i for i in items if i.name == "pasta")
        assert pasta_item.quantity == pytest.approx(800.0)

    # NOTE: multiple meals using the same ingredient (quantities summed) not tested
    # NOTE: empty meal plan (no meals) not tested
    # NOTE: ingredient with unit mismatch between inventory and recipe not tested


class TestMergeShoppingLists:
    def test_merge_combines_same_item(self):
        list1 = [ShoppingListItem("pasta", 200.0, Unit.GRAMS)]
        list2 = [ShoppingListItem("pasta", 300.0, Unit.GRAMS)]
        merged = merge_shopping_lists(list1, list2)
        assert len(merged) == 1
        assert merged[0].quantity == pytest.approx(500.0)

    # NOTE: merging items with different units (same name) not tested
    # NOTE: merging empty lists not tested
    # NOTE: merging more than two lists not tested
