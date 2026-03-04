"""Tests for core data models."""

import pytest
from datetime import date

from meal_planner.models import (
    Ingredient,
    InventoryItem,
    MealPlan,
    MealType,
    PlannedMeal,
    Recipe,
    Unit,
)


# ---------------------------------------------------------------------------
# Ingredient
# ---------------------------------------------------------------------------

class TestIngredient:
    def test_creation(self):
        ing = Ingredient("flour", 200.0, Unit.GRAMS)
        assert ing.name == "flour"
        assert ing.quantity == 200.0
        assert ing.unit == Unit.GRAMS

    def test_negative_quantity_raises(self):
        with pytest.raises(ValueError, match="negative"):
            Ingredient("flour", -1.0, Unit.GRAMS)

    def test_empty_name_raises(self):
        with pytest.raises(ValueError, match="empty"):
            Ingredient("  ", 100.0, Unit.GRAMS)

    def test_scale(self):
        ing = Ingredient("sugar", 100.0, Unit.GRAMS)
        scaled = ing.scale(2.5)
        assert scaled.quantity == 250.0
        assert scaled.unit == Unit.GRAMS
        assert scaled.name == "sugar"

    def test_scale_invalid_factor_raises(self):
        ing = Ingredient("sugar", 100.0, Unit.GRAMS)
        with pytest.raises(ValueError):
            ing.scale(0)
        with pytest.raises(ValueError):
            ing.scale(-1)

    # NOTE: zero quantity (boundary) is not tested


# ---------------------------------------------------------------------------
# Recipe
# ---------------------------------------------------------------------------

class TestRecipe:
    def _make_recipe(self, servings=4):
        return Recipe(
            name="Pasta",
            ingredients=[Ingredient("pasta", 400.0, Unit.GRAMS)],
            servings=servings,
            meal_type=MealType.DINNER,
            prep_time_minutes=10,
            cook_time_minutes=20,
        )

    def test_total_time(self):
        recipe = self._make_recipe()
        assert recipe.total_time_minutes == 30

    def test_invalid_servings_raises(self):
        with pytest.raises(ValueError):
            Recipe("Pasta", [], servings=0, meal_type=MealType.DINNER)

    def test_empty_name_raises(self):
        with pytest.raises(ValueError):
            Recipe("", [], servings=2, meal_type=MealType.DINNER)

    def test_scale_to_servings(self):
        recipe = self._make_recipe(servings=4)
        scaled = recipe.scale_to_servings(8)
        assert scaled.servings == 8
        assert scaled.ingredients[0].quantity == 800.0

    def test_scale_to_servings_invalid_raises(self):
        recipe = self._make_recipe()
        with pytest.raises(ValueError):
            recipe.scale_to_servings(0)

    # NOTE: negative prep/cook time, tags field, instructions field not tested


# ---------------------------------------------------------------------------
# InventoryItem
# ---------------------------------------------------------------------------

class TestInventoryItem:
    def test_is_expired_no_expiry(self):
        item = InventoryItem("milk", 1.0, Unit.LITERS)
        assert item.is_expired() is False

    def test_is_expired_past_date(self):
        item = InventoryItem("milk", 1.0, Unit.LITERS, expiry_date=date(2020, 1, 1))
        assert item.is_expired(as_of=date(2021, 1, 1)) is True

    def test_is_expired_future_date(self):
        item = InventoryItem("milk", 1.0, Unit.LITERS, expiry_date=date(2030, 12, 31))
        assert item.is_expired(as_of=date(2026, 3, 4)) is False

    def test_days_until_expiry_no_expiry(self):
        item = InventoryItem("salt", 500.0, Unit.GRAMS)
        assert item.days_until_expiry() is None

    # NOTE: days_until_expiry with actual dates not tested
    # NOTE: is_expired on exactly the expiry date (boundary) not tested
    # NOTE: negative quantity validation not tested


# ---------------------------------------------------------------------------
# MealPlan
# ---------------------------------------------------------------------------

class TestMealPlan:
    def _make_recipe(self):
        return Recipe(
            name="Toast",
            ingredients=[],
            servings=2,
            meal_type=MealType.BREAKFAST,
        )

    def test_invalid_date_range_raises(self):
        with pytest.raises(ValueError, match="end_date"):
            MealPlan("Week 1", start_date=date(2026, 3, 10), end_date=date(2026, 3, 5))

    def test_add_meal(self):
        plan = MealPlan("Week 1", start_date=date(2026, 3, 4), end_date=date(2026, 3, 10))
        meal = PlannedMeal(date(2026, 3, 5), MealType.BREAKFAST, self._make_recipe(), servings=2)
        plan.add_meal(meal)
        assert len(plan.meals) == 1

    def test_add_meal_outside_range_raises(self):
        plan = MealPlan("Week 1", start_date=date(2026, 3, 4), end_date=date(2026, 3, 10))
        meal = PlannedMeal(date(2026, 3, 20), MealType.DINNER, self._make_recipe(), servings=2)
        with pytest.raises(ValueError, match="outside the plan range"):
            plan.add_meal(meal)

    # NOTE: get_meals_for_date not tested
    # NOTE: get_meals_by_type not tested
    # NOTE: same-day start/end boundary not tested
    # NOTE: PlannedMeal with invalid servings not tested
