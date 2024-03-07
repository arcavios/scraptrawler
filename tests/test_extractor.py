import pytest
from scooze.card import Card
from scooze.deck import Deck

from scraptrawler.extractor import get_deck_from_url

# region Fixtures


@pytest.fixture
def goldfish_url() -> str:
    return "https://www.mtggoldfish.com/deck/5445907#paper"


@pytest.fixture
def mtg_decks_url() -> str:
    return "https://mtgdecks.net/Pioneer/boros-heroic-decklist-by-ibroadband-1572009/txt"


# endregion


# TODO: should probably parametrize this?
@pytest.mark("web")
def test_get_deck_from_url(goldfish_url, mtg_decks_url, deck_pioneer_heroic):
    goldfish_deck = get_deck_from_url(goldfish_url)
    assert goldfish_deck.decklist_equals(deck_pioneer_heroic)

    mtg_decks_deck = get_deck_from_url(mtg_decks_url)
    assert mtg_decks_deck.decklist_equals(deck_pioneer_heroic)
