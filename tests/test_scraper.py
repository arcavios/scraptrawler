from collections import Counter
from datetime import datetime
from typing import List

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scraptrawler.deck import Deck, Format
from scraptrawler.scraper.base import BaseScraper, LoadTime
from scraptrawler.scraper.melee import MeleeScraper, MeleeXPath
from scraptrawler.scraper.mtgo import MtgoScraper, MtgoXPath

# region Fixtures


@pytest.fixture
def test_main() -> Counter:
    return Counter(
        {
            "Katilda, Dawnhart Martyr // Katilda's Rising Dawn": 4,
            "Spirited Companion": 4,
            "Generous Visitor": 4,
            "Jukai Naturalist": 4,
            "Hallowed Haunting": 4,
            "The Restoration of Eiganjo // Architect of Restoration": 4,
            "Teachings of the Kirin // Kirin-Touched Orochi": 4,
            "Ossification": 4,
            "Wedding Announcement // Wedding Festivity": 2,
            "Commune with Spirits": 4,
            "Rite of Harmony": 1,
            "Forest": 5,
            "Plains": 5,
            "Brushland": 4,
            "Razorverge Thicket": 4,
            "Overgrown Farmland": 2,
            "Boseiju, Who Endures": 1,
        }
    )


@pytest.fixture
def test_side() -> Counter:
    return Counter(
        {
            "Circle of Confinement": 3,
            "Destroy Evil": 2,
            "Rite of Harmony": 2,
            "Wedding Announcement // Wedding Festivity": 2,
            "Vanquish the Horde": 2,
            "Nissa, Ascended Animist": 2,
            "Lantern Flare": 1,
            "Touch the Spirit Realm": 1,
        }
    )


@pytest.fixture
def melee_test_deck(test_main, test_side) -> Deck:
    test_deck = Deck(
        archetype="Selesnya Enchantments",
        format=Format.STANDARD,
        date_played=datetime.strptime("4/8/2023", "%m/%d/%Y"),
        main=test_main,
        side=test_side,
    )
    return test_deck


# region Scraper Fixtures


# maybe try again?
@pytest.fixture
def melee_scraper() -> MeleeScraper:
    melee_scraper = MeleeScraper()
    return melee_scraper


@pytest.fixture
def mtgo_scraper() -> MtgoScraper:
    mtgo_scraper = MtgoScraper()
    return mtgo_scraper


# endregion


# region Melee Fixtures
@pytest.fixture
def melee_deck_url() -> str:
    return "https://melee.gg/Decklist/View/290170"


@pytest.fixture
def melee_tournament_bad() -> str:
    return "https://melee.gg/Tournament/View/16153"


@pytest.fixture
def melee_tournament_small() -> str:
    return "https://melee.gg/Tournament/View/16031"


@pytest.fixture
def melee_tournament_large() -> str:
    return "https://melee.gg/Tournament/View/14149"


@pytest.fixture
def melee_tournaments(melee_tournament_small, melee_tournament_large) -> List[str]:
    return [melee_tournament_small, melee_tournament_large]


# endregion


# region MTGO Fixtures
@pytest.fixture
def mtgo_deck() -> str:
    return "https://www.mtgo.com/en/mtgo/decklist/pioneer-preliminary-2022-09-1512473564#deck_iBroadband"


@pytest.fixture
def mtgo_tournament() -> str:
    return "https://www.mtgo.com/en/mtgo/decklist/pioneer-super-qualifier-2022-10-0212480042"


@pytest.fixture
def mtgo_tournaments() -> List[str]:
    mtgo_tournaments = [  # List of all July 8 Challenge events
        # "https://www.mtgo.com/en/mtgo/decklist/pauper-challenge-2023-07-0812564209",  # July 8, 2023 - Pauper Challenge
        # "https://www.mtgo.com/en/mtgo/decklist/standard-challenge-32-2023-07-0812564211",  # July 8, 2023 - Standard Challenge
        "https://www.mtgo.com/en/mtgo/decklist/pioneer-challenge-2023-07-0812564215",  # July 8, 2023 - Pioneer Challenge
        "https://www.mtgo.com/en/mtgo/decklist/modern-challenge-2023-07-0812564212",  # July 8, 2023 - Modern Challenge
        "https://www.mtgo.com/en/mtgo/decklist/legacy-challenge-32-2023-07-0812564210",  # July 8, 2023 - Legacy Challenge
        # "https://www.mtgo.com/en/mtgo/decklist/vintage-challenge-2023-07-0812564213",  # July 8, 2023 - Vintage Challenge
    ]
    return mtgo_tournaments


# endregion
# endregion


@pytest.mark.web
@pytest.mark.slow
@pytest.mark.base_scraper
def test_base_scraper_load():
    url = "https://github.com/iambroadband/"
    scraper = BaseScraper()
    scraper._load(url)
    assert url == scraper.driver.current_url


@pytest.mark.web
@pytest.mark.slow
@pytest.mark.melee_scraper
def test_melee_scraper_wait_for_standings(melee_scraper, melee_tournament_large):
    melee_scraper._load(url=melee_tournament_large)
    deck_urls = melee_scraper._MeleeScraper__get_deck_urls_from_pagination()
    melee_scraper._MeleeScraper__set_per_page_max()
    melee_scraper._MeleeScraper__wait_for_standings()
    assert len(deck_urls) != len(melee_scraper._MeleeScraper__get_deck_urls_from_pagination())


@pytest.mark.web
@pytest.mark.slow
@pytest.mark.melee_scraper
def test_melee_scraper_get_deck_from_url(melee_scraper, melee_deck_url, melee_test_deck):
    deck = melee_scraper.get_deck_from_url(url=melee_deck_url)
    print(f"DECK: {deck.to_json()}")
    print(f"TEST_DECK: {melee_test_deck.to_json()}")
    assert deck == melee_test_deck


# TODO: Add more tests for Scrapers
