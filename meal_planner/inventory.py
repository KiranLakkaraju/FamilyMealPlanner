"""Inventory management for tracking pantry stock."""

from datetime import date
from typing import Dict, List, Optional, Tuple

from meal_planner.models import Ingredient, InventoryItem, Unit


class InventoryManager:
    """Manages the family pantry inventory."""

    def __init__(self):
        # Keyed by ingredient name (case-insensitive)
        self._items: Dict[str, InventoryItem] = {}

    def _key(self, name: str) -> str:
        return name.strip().lower()

    def add_item(self, item: InventoryItem) -> None:
        """Add or update an inventory item. Quantities are summed for existing items."""
        key = self._key(item.ingredient_name)
        if key in self._items:
            existing = self._items[key]
            if existing.unit != item.unit:
                raise ValueError(
                    f"Unit mismatch for '{item.ingredient_name}': "
                    f"existing={existing.unit}, new={item.unit}"
                )
            self._items[key] = InventoryItem(
                ingredient_name=existing.ingredient_name,
                quantity=existing.quantity + item.quantity,
                unit=existing.unit,
                expiry_date=item.expiry_date or existing.expiry_date,
            )
        else:
            self._items[key] = item

    def remove_item(self, name: str, quantity: float, unit: Unit) -> None:
        """Consume a quantity of an item from inventory."""
        key = self._key(name)
        if key not in self._items:
            raise KeyError(f"Item not found in inventory: '{name}'")
        item = self._items[key]
        if item.unit != unit:
            raise ValueError(
                f"Unit mismatch for '{name}': inventory={item.unit}, requested={unit}"
            )
        if item.quantity < quantity:
            raise ValueError(
                f"Insufficient quantity for '{name}': "
                f"available={item.quantity}, requested={quantity}"
            )
        new_qty = item.quantity - quantity
        if new_qty == 0:
            del self._items[key]
        else:
            self._items[key] = InventoryItem(
                ingredient_name=item.ingredient_name,
                quantity=new_qty,
                unit=item.unit,
                expiry_date=item.expiry_date,
            )

    def get_item(self, name: str) -> Optional[InventoryItem]:
        return self._items.get(self._key(name))

    def list_items(self) -> List[InventoryItem]:
        return list(self._items.values())

    def get_expired_items(self, as_of: Optional[date] = None) -> List[InventoryItem]:
        return [item for item in self._items.values() if item.is_expired(as_of)]

    def get_expiring_soon(
        self, days: int = 3, as_of: Optional[date] = None
    ) -> List[InventoryItem]:
        """Return items expiring within the given number of days."""
        result = []
        for item in self._items.values():
            days_left = item.days_until_expiry(as_of)
            if days_left is not None and 0 <= days_left <= days:
                result.append(item)
        return result

    def can_make_recipe(self, ingredients: List[Ingredient]) -> Tuple[bool, List[str]]:
        """
        Check if the inventory has enough of each ingredient to make a recipe.
        Returns (can_make, list_of_missing_or_insufficient_ingredients).
        """
        missing = []
        for ingredient in ingredients:
            item = self.get_item(ingredient.name)
            if item is None:
                missing.append(ingredient.name)
            elif item.unit != ingredient.unit:
                missing.append(f"{ingredient.name} (unit mismatch)")
            elif item.quantity < ingredient.quantity:
                missing.append(
                    f"{ingredient.name} (need {ingredient.quantity}, have {item.quantity})"
                )
        return (len(missing) == 0, missing)
