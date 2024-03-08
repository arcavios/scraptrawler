import pytest
from scraptrawler.extractor import get_deck_from_url

# region Fixtures


@pytest.fixture
def goldfish_url() -> str:
    return "https://www.mtggoldfish.com/deck/5445907#paper"


@pytest.fixture
def mtg_decks_url() -> str:
    return "https://mtgdecks.net/Pioneer/boros-heroic-decklist-by-ibroadband-1572009"


@pytest.fixture
def mtg_top8_url() -> str:
    return "https://www.mtgtop8.com/event?e=41739&d=509967&f=PI"


@pytest.fixture
def scryfall_url() -> str:
    return "https://scryfall.com/@iBroadband/decks/ceaf6b1d-97e5-47fb-9a7d-c7f116554ad2"


@pytest.fixture
def tappedout_url() -> str:
    return "https://tappedout.net/mtg-decks/boros-heroic-pioneer-preliminary-feb-27-2023-2"


# endregion


# TODO: should probably parametrize this?
@pytest.mark.web
def test_get_deck_from_url(goldfish_url, mtg_decks_url, mtg_top8_url, scryfall_url, tappedout_url, deck_pioneer_heroic):
    goldfish_deck = get_deck_from_url(goldfish_url)
    assert goldfish_deck.decklist_equals(deck_pioneer_heroic)

    mtg_decks_deck = get_deck_from_url(mtg_decks_url)
    assert mtg_decks_deck.decklist_equals(deck_pioneer_heroic)

    mtg_top8_deck = get_deck_from_url(mtg_top8_url)
    assert mtg_top8_deck.decklist_equals(deck_pioneer_heroic)

    scryfall_deck = get_deck_from_url(scryfall_url)
    assert scryfall_deck.decklist_equals(deck_pioneer_heroic)

    tappedout_deck = get_deck_from_url(tappedout_url)
    assert tappedout_deck.decklist_equals(deck_pioneer_heroic)
