import pytest
from app.domain.foods.rules import normalize_ingredients, suspect_ingredients

pytestmark = pytest.mark.req("5.3.5")


def test_normalize_trims_and_drops_blanks_and_case_insensitive_duplicates():
    assert normalize_ingredients(["  Курица ", "рис", "КУРИЦА", "", "   ", "рыбий  жир"]) == [
        "Курица",
        "рис",
        "рыбий жир",
    ]


@pytest.mark.req("5.3.3")
def test_suspects_ignore_case_and_spacing_and_keep_order():
    tolerated = [["курица", "Рис"], ["рыбий жир"]]
    assert suspect_ingredients(["Горох", "КУРИЦА", "Рыбий  жир", "Утка"], tolerated) == ["Горох", "Утка"]


@pytest.mark.req("5.3.3")
def test_everything_is_suspect_without_tolerated_history():
    assert suspect_ingredients(["Курица"], []) == ["Курица"]
