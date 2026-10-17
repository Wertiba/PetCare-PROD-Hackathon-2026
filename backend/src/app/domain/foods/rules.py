from collections.abc import Iterable


def ingredient_key(ingredient: str) -> str:
    """ "Курица ", "курица" and "КУРИЦА" are one ingredient."""
    return " ".join(ingredient.split()).casefold()


def normalize_ingredients(ingredients: Iterable[str]) -> list[str]:
    """Trim, drop blanks and case-insensitive duplicates, keep the first spelling and the order."""
    seen: set[str] = set()
    result: list[str] = []
    for ingredient in ingredients:
        cleaned = " ".join(ingredient.split())
        key = cleaned.casefold()
        if key and key not in seen:
            seen.add(key)
            result.append(cleaned)
    return result


def suspect_ingredients(ingredients: Iterable[str], tolerated: Iterable[Iterable[str]]) -> list[str]:
    """Ingredients that no previously tolerated food contained: the likely cause of a bad reaction."""
    known = {ingredient_key(ingredient) for food in tolerated for ingredient in food}
    return [ingredient for ingredient in ingredients if ingredient_key(ingredient) not in known]
