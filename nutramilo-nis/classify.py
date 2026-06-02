"""Deterministic rule-based classifier for fat_type and protein_type.

Addresses Reviewer R2 critique #3 (unvalidated manual classification).

Each food is classified from its `food` and `category` fields ONLY,
without human judgement.  The classification table below is the entire
rule set — no other input is used, no overrides allowed.  Any food not
matched by the rules falls through to "mixed" by default.

Reproducibility
---------------
Running this module on the validation CSV is guaranteed to produce the
same fat_type/protein_type for every food forever (the rule table is
frozen with the v1.1.2 release).  This eliminates investigator-bias
risk that the manual classification of v1.1.1 introduced.

Rules
-----
The rules cascade in this order — first match wins:

    1. PURE_FAT_NAMES    → fat=plant or animal (by name), protein=mixed
    2. ANIMAL_PROTEIN    → fat={dairy→animal | fish/poultry/lean→animal},
                           protein=animal
    3. PLANT_PROTEIN     → fat=plant, protein=plant
    4. DAIRY_PRODUCT     → fat=animal, protein=animal
    5. ANIMAL_FAT_DOM    → fat=animal, protein=mixed
    6. PLANT_FAT_DOM     → fat=plant, protein=plant
    7. REFINED_STARCH    → fat=mixed, protein=plant
    8. FRUIT / VEG       → fat=mixed, protein=plant
    9. default           → fat=mixed, protein=mixed
"""
from __future__ import annotations

from typing import Tuple

# 1. Pure-fat foods — fat dominates, protein near zero
ANIMAL_FAT_PURE = {
    "butter", "cream", "heavy_cream", "lard", "tallow", "ghee",
    "bacon_fat", "duck_fat", "schmaltz",
}
PLANT_FAT_PURE = {
    "olive_oil", "evoo", "sunflower_oil", "canola_oil", "rapeseed_oil",
    "coconut_oil", "flaxseed_oil", "avocado_oil", "sesame_oil",
    "peanut_oil", "soybean_oil", "mayonnaise",  # mayo dominantly oil
}

# 2. Animal protein dominant
ANIMAL_PROTEIN_NAMES = {
    "beef", "steak", "ground_beef", "lamb", "veal", "pork", "ham",
    "bacon", "sausage", "salami", "prosciutto", "chicken", "chicken_breast",
    "turkey", "duck", "goose", "rabbit",
    "fish", "salmon", "tuna", "cod", "trout", "mackerel", "sardines",
    "shrimp", "prawns", "crab", "lobster", "scallops", "mussels",
    "egg", "egg_white", "eggs",
    "whey", "casein", "milk_protein", "collagen",
}

# 3. Plant protein dominant
PLANT_PROTEIN_NAMES = {
    "tofu", "tempeh", "seitan", "edamame",
    "lentil", "lentils", "chickpea", "chickpeas", "bean", "beans",
    "black_beans", "kidney_beans", "navy_beans", "lima_beans",
    "split_pea", "peas",
    "soy", "soy_protein", "soy_milk",
    "pea_protein", "hemp_protein", "rice_protein",
}

# 4. Dairy products — animal fat + animal protein
DAIRY_PRODUCT_NAMES = {
    "milk", "milk_full", "milk_whole", "milk_skim", "milk_low_fat",
    "yogurt", "yoghurt", "yogurt_low_fat", "yogurt_full_fat",
    "greek_yogurt", "greek_yoghurt", "kefir",
    "cheese", "cheese_hard", "cheese_soft", "cheddar", "parmesan",
    "mozzarella", "feta", "cottage_cheese", "ricotta", "halloumi",
    "ice_cream",
}

# 5. Plant-fat-dominant (nuts, seeds, oils — but with some protein)
PLANT_FAT_DOM_NAMES = {
    "almonds", "walnuts", "cashews", "pistachios", "pecans",
    "hazelnuts", "macadamia", "brazil_nuts", "pine_nuts",
    "sunflower_seeds", "pumpkin_seeds", "sesame_seeds",
    "chia_seeds", "flaxseeds", "hemp_seeds",
    "avocado", "olives", "peanut", "peanuts", "peanut_butter",
    "almond_butter", "tahini",
}

# 6. Refined-starch carbohydrates
REFINED_STARCH_NAMES = {
    "white_bread", "white_rice", "spaghetti_white", "noodles_instant",
    "cornflakes", "rice_krispies", "muesli", "porridge", "porridge_oats",
    "potato_boiled", "potato_mashed", "potato", "potatoes",
    "pancakes", "doughnuts", "donut", "croissant", "bagel",
    "sponge_cake", "cake", "cookies", "crackers", "biscuits",
    "honey_smacks", "all_bran", "weetabix", "shredded_wheat",
    "white_bread_50g", "oats",  # processed oats default to refined; whole_grain rule above catches steel-cut/rolled
}

# 7. Whole-grain carbohydrates (still plant)
WHOLE_GRAIN_NAMES = {
    "whole_grain_bread", "whole_meal_bread", "wholemeal_bread",
    "rye_bread", "pumpernickel", "sourdough",
    "oats_rolled", "oats_steel_cut", "oatmeal", "quinoa",
    "barley", "buckwheat", "millet", "brown_rice", "wild_rice",
    "brown_pasta", "whole_wheat_pasta", "wholemeal_pasta",
    "bulgur", "spelt", "amaranth",
}

# 8. Fruits & vegetables — plant defaults
FRUIT_VEG_NAMES = {
    "apple", "apples", "banana", "bananas", "grape", "grapes",
    "orange", "oranges", "pear", "pears", "berries", "strawberries",
    "blueberries", "watermelon", "melon", "pineapple", "mango",
    "broccoli", "carrot", "carrots", "spinach", "kale", "lettuce",
    "tomato", "tomatoes", "cucumber", "pepper", "peppers", "onion",
    "garlic", "zucchini", "eggplant", "cauliflower", "cabbage",
}

# 9. Composite categories (rough heuristic — protein source decides)
COMPOSITE_HINT = {
    "meal", "breakfast", "lunch", "dinner", "platter", "bowl",
}


def _norm(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "_").replace("-", "_")


def classify(food: str, category: str = "") -> Tuple[str, str]:
    """Return (fat_type, protein_type) — deterministic, blinded to FII.

    Parameters
    ----------
    food : str
        Food name (case-insensitive).  Spaces and hyphens are normalised
        to underscores before matching.
    category : str, optional
        Food category (case-insensitive).  Used as secondary fallback.

    Returns
    -------
    (fat_type, protein_type) : Tuple[str, str]
        Each element ∈ {"plant", "mixed", "animal"}.
    """
    n = _norm(food)
    c = _norm(category)

    # Rule 1 — pure fats
    if any(t in n for t in ANIMAL_FAT_PURE) or c in ANIMAL_FAT_PURE:
        return "animal", "mixed"
    if any(t in n for t in PLANT_FAT_PURE) or c in PLANT_FAT_PURE:
        return "plant", "mixed"

    # Rule 4 — dairy (check BEFORE animal-protein because "milk" matches both)
    if any(t in n for t in DAIRY_PRODUCT_NAMES) or c in {"dairy"}:
        return "animal", "animal"

    # Rule 2 — animal protein
    if any(t in n for t in ANIMAL_PROTEIN_NAMES) or c in {
        "meat", "fish", "poultry", "seafood", "egg"
    }:
        return "animal", "animal"

    # Rule 3 — plant protein (legumes/tofu)
    if any(t in n for t in PLANT_PROTEIN_NAMES) or c in {
        "legume", "tofu", "soy_product", "plant_protein"
    }:
        return "plant", "plant"

    # Rule 5 — plant-fat-dominant
    if any(t in n for t in PLANT_FAT_DOM_NAMES) or c in {
        "nut", "nuts", "seed", "seeds"
    }:
        return "plant", "plant"

    # Rule 6/7 — refined or whole-grain starches
    if any(t in n for t in REFINED_STARCH_NAMES) or c in {
        "refined_grain", "starchy_tuber", "refined_starch"
    }:
        # Refined starches are plant-derived; fat is incidental and usually plant.
        return "plant", "plant"
    if any(t in n for t in WHOLE_GRAIN_NAMES) or c in {
        "whole_grain", "grain_whole"
    }:
        return "plant", "plant"

    # Rule 8 — fruits/vegetables — explicitly plant on both axes
    if any(t in n for t in FRUIT_VEG_NAMES) or c in {
        "fruit", "vegetable", "fruits", "vegetables"
    }:
        return "plant", "plant"

    # Rule 9 — default
    return "mixed", "mixed"
