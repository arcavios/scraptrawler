from datetime import datetime
from typing import Counter, List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from strenum import StrEnum

from scraptrawler.deck import Deck, Format, InThe
from scraptrawler.scraper.base import BaseScraper, LoadTime
from scraptrawler.utils import Constants, ExtendedEnum, get_logger


class MtgoXPath(ExtendedEnum, StrEnum):
    """
    A class used for storing XPath related to MTGO and its DOM elements.

    Deck Parts
    ----------
    DECK : Deck part elements.
    MAIN : Main deck elements.
    SIDE : Sideboard elements.
    CARD : Card elements. Includes name and quantity.
    """

    # Event info
    DATE = "//p[@class='decklist-posted-on']"

    # Deck parts
    CARD = ".//a[@class='decklist-card-link']"
    DECK = "//div[@class='decklist-sort-group decklist-sort-type']"
    MAIN = DECK + "//div[@class='decklist-category-columns']"
    SIDE = DECK + "//ul[@class='decklist-category-list decklist-sideboard decklist-category-columns']"


class MtgoScraper(BaseScraper):
    """
    A class to represent a type of Scraper used to get data about
    Magic: the Gathering decklists and results from [MTGO](https://mtgo.com).

    Attributes
    ----------
    webdriver : webdriver.Remote
        Controls a browser by sending commands to a remote server.

    Methods
    -------
    get_decks_from_event_url(url: str, top8: bool):
        Returns a list of Decks from the given event URL.
    get_deck_from_url(url: str):
        Returns a Deck from the given deck page URL.
    """

    def __init__(self, driver: webdriver.Remote = None):
        self.logger = get_logger(self.log_filename, "MtgoScraper")
        super().__init__(driver=driver, logger=self.logger)

    ### Public Function Overrides

    def get_decks_from_event_url(self, url: str, top8: bool = False) -> List[Deck]:
        # Get page
        self._load(url)
        event_name = self._sanitized_title()
        self.logger.info(f"{url} - Processing event - {event_name}.")

        ## Get Deck parts

        # Archetype
        # TODO: get archetype with db api maybe?
        # deck_archetype = Deck.DEFAULT_ARCHETYPE

        # Format
        deck_format = Format.get(event_name.split(" ")[0])

        # Date
        date_played_element = WebDriverWait(self.driver, LoadTime.STD).until(
            EC.presence_of_element_located((By.XPATH, MtgoXPath.DATE))
        )
        date_played = datetime.strptime(
            date_played_element.text.replace("Posted on ", "").strip(), Constants.MTGO_DATE_FORMAT
        )

        # Get cards and quantities from the page
        main_elements = WebDriverWait(self.driver, LoadTime.STD).until(
            EC.presence_of_all_elements_located((By.XPATH, MtgoXPath.MAIN))
        )
        side_elements = WebDriverWait(self.driver, LoadTime.STD).until(
            EC.presence_of_all_elements_located((By.XPATH, MtgoXPath.SIDE))
        )

        decks = self._decks_from_elements(
            deck_format=deck_format, date_played=date_played, main_elements=main_elements, side_elements=side_elements
        )
        # FIXME: Is it faster to have this run against main_elements and side_elements?
        if top8:
            decks = decks[:8]

        return decks

    def get_deck_from_url(self, url: str) -> Deck:
        # Get page
        self._load(url)
        event_name = self._sanitized_title()
        self.logger.info(f"{url} - Processing deck from event - {event_name}.")

        ## Get cards and quantities from the page
        # Setup XPATH
        player = url.split("#deck_")[-1]
        player_XPATH = f"//a[@href='#deck_{player}']/ancestor::section"

        ## Get Deck parts

        # Archetype
        # TODO: get archetype with db api maybe?
        deck_archetype = Deck.DEFAULT_ARCHETYPE

        # Format
        deck_format = Format.get(event_name.split(" ")[0])

        # Date
        date_played_element = WebDriverWait(self.driver, LoadTime.STD).until(
            EC.presence_of_element_located((By.XPATH, MtgoXPath.DATE))
        )
        date_played = datetime.strptime(
            date_played_element.text.replace("Posted on ", "").strip(), Constants.MTGO_DATE_FORMAT
        )

        # Get deck from main and side elements
        main_element = WebDriverWait(self.driver, LoadTime.STD).until(
            EC.presence_of_element_located((By.XPATH, player_XPATH + MtgoXPath.MAIN))
        )
        side_element = WebDriverWait(self.driver, LoadTime.STD).until(
            EC.presence_of_element_located((By.XPATH, player_XPATH + MtgoXPath.SIDE))
        )

        # Build Deck
        deck = self._deck_from_parts(main_element, side_element)
        deck.archetype = deck_archetype
        deck.format = deck_format
        deck.date_played = date_played

        return deck

    ### Protected Function Overrides

    def _sanitized_title(self) -> str:
        try:
            title = self.driver.find_element(By.CLASS_NAME, "decklist-title").text
            date = self.driver.find_element(By.CLASS_NAME, "decklist-posted-on").text
            return f"{title} - {date.replace('Posted on ', '')}"
        except Exception as e:
            # raise (e)
            self.logger.warning(f"{self.driver.current_url} - Unable to sanitize title. Proceeding with defaults.")
            return ""

    def _decks_from_elements(
        self,
        deck_format: Format,
        date_played: datetime,
        main_elements: List[WebElement],
        side_elements: List[WebElement],
    ) -> List[Deck]:
        # Sanity check there are the same number of main decks and sideboards
        num_mains, num_sides = len(main_elements), len(side_elements)
        if num_mains != num_sides:
            self.logger.warning(
                f"""{self.driver.current_url} - There are {num_mains} main decks and {num_sides} sideboards."""
                f"""This may cause problems."""
            )

        decks: List[Deck] = []
        for i in range(len(main_elements)):
            # Get a deck from WebElements
            deck = self._deck_from_parts(main_elements[i], side_elements[i])
            # deck.archetype = deck_archetype # TODO
            deck.format = deck_format
            deck.date_played = date_played
            decks.append(deck)

        return decks

    def _deck_from_parts(self, main_element: WebElement, side_element: WebElement) -> Deck:
        main_cards = self._cards_from_element(main_element)
        side_cards = self._cards_from_element(side_element)

        # Create a Deck
        deck = Deck()
        deck.add_cards(cards=main_cards, in_the=InThe.MAIN)
        deck.add_cards(cards=side_cards, in_the=InThe.SIDE)

        return deck

    def _cards_from_element(self, deck_element: WebElement) -> List[Counter]:
        card_elements = WebDriverWait(deck_element, LoadTime.STD).until(
            EC.presence_of_all_elements_located((By.XPATH, MtgoXPath.CARD))
        )

        cards = Counter()
        for ce in card_elements:
            quantity, card = ce.text.split(" ", maxsplit=1)
            cards.update({card: int(quantity)})

        return cards
