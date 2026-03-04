"""Tests for RecipeBook."""

import pytest

from meal_planner.models import Ingredient, MealType, Recipe, Unit
from meal_planner.recipe_book import RecipeBook


def make_recipe(name="Pancakes", meal_type=MealType.BREAKFAST, tags=None, total_time=30):
    prep = total_time // 2
    cook = total_time - prep
    return Recipe(
        name=name,
        ingredients=[Ingredient("flour", 200.0, Unit.GRAMS)],
        servings=2,
        meal_type=meal_type,
        prep_time_minutes=prep,
        cook_time_minutes=cook,
        tags=tags or [],
    )


@pytest.fixture
def book():
    rb = RecipeBook()
    rb.add_recipe(make_recipe("Pancakes", MealType.BREAKFAST, tags=["quick", "vegetarian"]))
    rb.add_recipe(make_recipe("Grilled Chicken", MealType.DINNER, tags=["protein"]))
    rb.add_recipe(make_recipe("Caesar Salad", MealType.LUNCH, tags=["vegetarian"], total_time=15))
    return rb


class TestAddAndGet:
    def test_add_and_get(self, book):
        recipe = book.get_recipe("Pancakes")
        assert recipe is not None
        assert recipe.name == "Pancakes"

    def test_add_duplicate_raises(self, book):
        with pytest.raises(ValueError, match="already exists"):
            book.add_recipe(make_recipe("Pancakes"))

    def test_get_nonexistent_returns_none(self, book):
        assert book.get_recipe("Pizza") is None

    # NOTE: case-insensitive get not tested
    # NOTE: update_recipe not tested at all
    # NOTE: remove_recipe not tested at all


class TestSearch:
    def test_search_by_meal_type(self, book):
        results = book.search_by_meal_type(MealType.BREAKFAST)
        assert len(results) == 1
        assert results[0].name == "Pancakes"

    def test_search_by_tag(self, book):
        results = book.search_by_tag("vegetarian")
        names = {r.name for r in results}
        assert names == {"Pancakes", "Caesar Salad"}

    def test_search_by_tag_case_insensitive(self, book):
        results = book.search_by_tag("VEGETARIAN")
        assert len(results) == 2

    def test_search_by_max_time(self, book):
        results = book.search_by_max_time(20)
        assert len(results) == 1
        assert results[0].name == "Caesar Salad"

    # NOTE: search_by_ingredient is entirely untested
    # NOTE: search returning empty list not tested
    # NOTE: search_by_meal_type with no matching recipes not tested
