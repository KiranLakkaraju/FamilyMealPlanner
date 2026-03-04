"""Tests for InventoryManager."""

import pytest
from datetime import date

from meal_planner.inventory import InventoryManager
from meal_planner.models import Ingredient, InventoryItem, Unit


@pytest.fixture
def inventory():
    mgr = InventoryManager()
    mgr.add_item(InventoryItem("flour", 500.0, Unit.GRAMS))
    mgr.add_item(InventoryItem("milk", 2.0, Unit.LITERS))
    return mgr


class TestAddItem:
    def test_add_new_item(self, inventory):
        inventory.add_item(InventoryItem("eggs", 6.0, Unit.PIECES))
        assert inventory.get_item("eggs") is not None

    def test_add_existing_item_sums_quantity(self, inventory):
        inventory.add_item(InventoryItem("flour", 200.0, Unit.GRAMS))
        assert inventory.get_item("flour").quantity == 700.0

    def test_add_case_insensitive(self, inventory):
        inventory.add_item(InventoryItem("Flour", 100.0, Unit.GRAMS))
        assert inventory.get_item("flour").quantity == 600.0

    def test_add_unit_mismatch_raises(self, inventory):
        with pytest.raises(ValueError, match="Unit mismatch"):
            inventory.add_item(InventoryItem("flour", 1.0, Unit.KILOGRAMS))

    # NOTE: expiry_date merging logic (which date wins) is not tested


class TestRemoveItem:
    def test_remove_partial(self, inventory):
        inventory.remove_item("flour", 200.0, Unit.GRAMS)
        assert inventory.get_item("flour").quantity == 300.0

    def test_remove_exact_quantity_deletes_item(self, inventory):
        inventory.remove_item("flour", 500.0, Unit.GRAMS)
        assert inventory.get_item("flour") is None

    def test_remove_nonexistent_raises(self, inventory):
        with pytest.raises(KeyError):
            inventory.remove_item("sugar", 100.0, Unit.GRAMS)

    def test_remove_insufficient_quantity_raises(self, inventory):
        with pytest.raises(ValueError, match="Insufficient"):
            inventory.remove_item("flour", 1000.0, Unit.GRAMS)

    # NOTE: remove with unit mismatch is not tested


class TestExpiryQueries:
    def test_get_expired_items(self):
        mgr = InventoryManager()
        mgr.add_item(InventoryItem("old_milk", 1.0, Unit.LITERS, expiry_date=date(2020, 1, 1)))
        mgr.add_item(InventoryItem("fresh_juice", 1.0, Unit.LITERS, expiry_date=date(2030, 1, 1)))
        expired = mgr.get_expired_items(as_of=date(2026, 3, 4))
        assert len(expired) == 1
        assert expired[0].ingredient_name == "old_milk"

    # NOTE: get_expiring_soon is entirely untested
    # NOTE: items with no expiry date are not verified to be excluded from expired list


class TestCanMakeRecipe:
    def test_can_make_when_sufficient(self, inventory):
        ingredients = [
            Ingredient("flour", 300.0, Unit.GRAMS),
            Ingredient("milk", 1.0, Unit.LITERS),
        ]
        can_make, missing = inventory.can_make_recipe(ingredients)
        assert can_make is True
        assert missing == []

    def test_cannot_make_when_ingredient_missing(self, inventory):
        ingredients = [Ingredient("eggs", 2.0, Unit.PIECES)]
        can_make, missing = inventory.can_make_recipe(ingredients)
        assert can_make is False
        assert "eggs" in missing

    # NOTE: unit mismatch case in can_make_recipe not tested
    # NOTE: insufficient quantity (item exists but not enough) not tested
    # NOTE: empty ingredient list (edge case) not tested
