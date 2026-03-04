"""Core data models for the FamilyMealPlanner."""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional


class MealType(Enum):
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


class Unit(Enum):
    GRAMS = "g"
    KILOGRAMS = "kg"
    MILLILITERS = "ml"
    LITERS = "l"
    PIECES = "pcs"
    TABLESPOONS = "tbsp"
    TEASPOONS = "tsp"
    CUPS = "cups"


@dataclass
class Ingredient:
    name: str
    quantity: float
    unit: Unit

    def __post_init__(self):
        if self.quantity < 0:
            raise ValueError(f"Ingredient quantity cannot be negative: {self.quantity}")
        if not self.name.strip():
            raise ValueError("Ingredient name cannot be empty")

    def scale(self, factor: float) -> "Ingredient":
        """Return a new Ingredient scaled by the given factor."""
        if factor <= 0:
            raise ValueError(f"Scale factor must be positive: {factor}")
        return Ingredient(self.name, self.quantity * factor, self.unit)


@dataclass
class Recipe:
    name: str
    ingredients: List[Ingredient]
    servings: int
    meal_type: MealType
    instructions: str = ""
    prep_time_minutes: int = 0
    cook_time_minutes: int = 0
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.name.strip():
            raise ValueError("Recipe name cannot be empty")
        if self.servings <= 0:
            raise ValueError(f"Servings must be positive: {self.servings}")
        if self.prep_time_minutes < 0 or self.cook_time_minutes < 0:
            raise ValueError("Time values cannot be negative")

    @property
    def total_time_minutes(self) -> int:
        return self.prep_time_minutes + self.cook_time_minutes

    def scale_to_servings(self, desired_servings: int) -> "Recipe":
        """Return a new Recipe scaled to the desired number of servings."""
        if desired_servings <= 0:
            raise ValueError(f"Desired servings must be positive: {desired_servings}")
        factor = desired_servings / self.servings
        scaled_ingredients = [ing.scale(factor) for ing in self.ingredients]
        return Recipe(
            name=self.name,
            ingredients=scaled_ingredients,
            servings=desired_servings,
            meal_type=self.meal_type,
            instructions=self.instructions,
            prep_time_minutes=self.prep_time_minutes,
            cook_time_minutes=self.cook_time_minutes,
            tags=list(self.tags),
        )


@dataclass
class InventoryItem:
    ingredient_name: str
    quantity: float
    unit: Unit
    expiry_date: Optional[date] = None

    def __post_init__(self):
        if self.quantity < 0:
            raise ValueError(f"Inventory quantity cannot be negative: {self.quantity}")
        if not self.ingredient_name.strip():
            raise ValueError("Ingredient name cannot be empty")

    def is_expired(self, as_of: Optional[date] = None) -> bool:
        """Return True if the item is expired as of the given date (defaults to today)."""
        if self.expiry_date is None:
            return False
        check_date = as_of if as_of is not None else date.today()
        return self.expiry_date < check_date

    def days_until_expiry(self, as_of: Optional[date] = None) -> Optional[int]:
        """Return the number of days until expiry, or None if no expiry date."""
        if self.expiry_date is None:
            return None
        check_date = as_of if as_of is not None else date.today()
        return (self.expiry_date - check_date).days


@dataclass
class PlannedMeal:
    date: date
    meal_type: MealType
    recipe: Recipe
    servings: int

    def __post_init__(self):
        if self.servings <= 0:
            raise ValueError(f"Servings must be positive: {self.servings}")


@dataclass
class MealPlan:
    name: str
    start_date: date
    end_date: date
    meals: List[PlannedMeal] = field(default_factory=list)

    def __post_init__(self):
        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")

    def add_meal(self, meal: PlannedMeal) -> None:
        if meal.date < self.start_date or meal.date > self.end_date:
            raise ValueError(
                f"Meal date {meal.date} is outside the plan range "
                f"[{self.start_date}, {self.end_date}]"
            )
        self.meals.append(meal)

    def get_meals_for_date(self, target_date: date) -> List[PlannedMeal]:
        return [m for m in self.meals if m.date == target_date]

    def get_meals_by_type(self, meal_type: MealType) -> List[PlannedMeal]:
        return [m for m in self.meals if m.meal_type == meal_type]
