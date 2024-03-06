import pytest
from scraptrawler.extractor import get_deck_from_url
from scooze.card import Card
from scooze.deck import Deck

# region Fixtures


@pytest.fixture
def goldfish_url() -> str:
    return "https://www.mtggoldfish.com/deck/5445907#paper"


# endregion


def test_get_deck_from_url_goldfish(goldfish_url, deck_pioneer_heroic):
    deck = get_deck_from_url(goldfish_url)

    assert deck.decklist_equals(deck_pioneer_heroic)
