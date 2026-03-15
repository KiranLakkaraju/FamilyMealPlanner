# FamilyMealPlanner

A family meal planner web application built with Flask and SQLite. Plan weekly meals, manage recipes, track pantry inventory, and generate shopping lists.

## Features

- **Weekly Meal Planning** - Drag-and-drop style weekly calendar with breakfast, lunch, dinner, and snack slots
- **Recipe Management** - Create, edit, and organize recipes with ingredients and instructions
- **Pantry Inventory** - Track what you have on hand, organized by category
- **Shopping List** - Auto-generate from your meal plan, with manual additions and purchase tracking
- **Family Profiles** - Track preferences and allergies for each family member

## Setup

```bash
pip install -r requirements.txt
python app.py
```

Then open http://localhost:5000 in your browser.

### Load Sample Data

```bash
python seed_data.py
```

This adds sample recipes, family members, inventory items, and a week of planned meals.
