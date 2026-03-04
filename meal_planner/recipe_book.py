"""Recipe book for storing and searching recipes."""

from typing import Dict, List, Optional

from meal_planner.models import MealType, Recipe


class RecipeBook:
    """A collection of recipes with search and filter capabilities."""

    def __init__(self):
        self._recipes: Dict[str, Recipe] = {}

    def _key(self, name: str) -> str:
        return name.strip().lower()

    def add_recipe(self, recipe: Recipe) -> None:
        key = self._key(recipe.name)
        if key in self._recipes:
            raise ValueError(f"Recipe already exists: '{recipe.name}'")
        self._recipes[key] = recipe

    def update_recipe(self, recipe: Recipe) -> None:
        key = self._key(recipe.name)
        if key not in self._recipes:
            raise KeyError(f"Recipe not found: '{recipe.name}'")
        self._recipes[key] = recipe

    def remove_recipe(self, name: str) -> None:
        key = self._key(name)
        if key not in self._recipes:
            raise KeyError(f"Recipe not found: '{name}'")
        del self._recipes[key]

    def get_recipe(self, name: str) -> Optional[Recipe]:
        return self._recipes.get(self._key(name))

    def list_recipes(self) -> List[Recipe]:
        return list(self._recipes.values())

    def search_by_tag(self, tag: str) -> List[Recipe]:
        tag_lower = tag.strip().lower()
        return [r for r in self._recipes.values() if tag_lower in [t.lower() for t in r.tags]]

    def search_by_meal_type(self, meal_type: MealType) -> List[Recipe]:
        return [r for r in self._recipes.values() if r.meal_type == meal_type]

    def search_by_ingredient(self, ingredient_name: str) -> List[Recipe]:
        name_lower = ingredient_name.strip().lower()
        return [
            r
            for r in self._recipes.values()
            if any(i.name.lower() == name_lower for i in r.ingredients)
        ]

    def search_by_max_time(self, max_minutes: int) -> List[Recipe]:
        return [r for r in self._recipes.values() if r.total_time_minutes <= max_minutes]
