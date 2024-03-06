from collections import namedtuple
from datetime import datetime
from typing import Counter, List

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from strenum import StrEnum

from scraptrawler.deck import Deck, Format, InThe
from scraptrawler.scraper.base import BaseScraper, LoadTime
from scraptrawler.utils import Constants, ExtendedEnum, get_logger


class MeleeXPath(ExtendedEnum, StrEnum):
    """
    A class used for storing XPath related to MTG Melee and its DOM elements.

    Deck Parts
    ----------
    MAIN : Main deck elements.
    SIDE : Sideboard element.
    QTY : Card quantity elements.
    CARD : Card name elements.
    QTY_DATA : The attribute containing the relevant quantity data.
    CARD_DATA : The attribute containing the relevant card name data.

    Page Info
    ----------
    TOURNAMENT_HEADLINE : Headline at the top of a tournament page. Has date, registration, and other information.

    Standings Table
    ----------
    DECK_URL : Deck URL elements.
    PROCESSING_LBL : Label that appears when the tournament standings table is loading.

    Pagination
    ----------
    PAGINATE_BTN : The page # buttons at the bottom of the tournament standings table.
    PER_PAGE_MAX_OPT : The maximum per-page option.
    PER_PAGE_SELECT : The select tag that determines how many deck URLs are on each page of the tournament standings
    table.
    """

    # Deck parts
    DATE_PLAYED = "//*[local-name() = 'svg'][@data-icon='calendar-days']/parent::div"
    DECK_FORMAT = "//*[local-name() = 'svg'][@data-icon='fort-awesome']/parent::div"
    MAIN = (
        "//tr//td[@class='decklist-builder-section-label-cell']"
        "[not(text() = 'Sideboard')][not(text() = 'Companion')]"
        "/ancestor::table"
    )
    SIDE = "//tr//td[@class='decklist-builder-section-label-cell'][text() = 'Sideboard']/ancestor::table"
    QTY = ".//td[@class='decklist-builder-card-quantity-cell']"
    CARD = ".//a[@data-type='card']"
    QTY_DATA = "innerHTML"
    CARD_DATA = "data-name"

    # Page info
    ACCEPT_COOKIES_BTN = "//div[@class='d-flex flex-row-reverse']//input"
    TOURNAMENT_HEADLINE = "//p[@id='tournament-headline-registration']"

    # Standings table
    DECK_URL = "//table[@id='tournament-standings-table']//a[@data-type='decklist']"
    PROCESSING_LBL = "//div[@id='tournament-standings-table_processing']"

    # Pagination
    PAGINATE_BTN = "//span//a[contains(@class, 'paginate_button')][@aria-controls='tournament-standings-table']"
    PER_PAGE_MAX_OPT = "//select[@aria-controls='tournament-standings-table']//option[@value='500']"
    PER_PAGE_SELECT = "//select[@aria-controls='tournament-standings-table']"


class MeleeScraper(BaseScraper):
    """
    A class to represent a type of Scraper used to get data about Magic: the Gathering decklists and results from
    [MTG Melee](https://melee.gg).

    Attributes
    ----------
    driver : webdriver.Remote
        Controls a browser by sending commands to a remote server.

    Methods
    -------
    get_event_slots_from_event_url(url: str)
        Returns a tuple of (slots_remaining, total_slots)
    get_decks_from_event_url(url: str, top8: bool):
        Returns a list of Decks from the given event URL.
    get_deck_from_url(url: str):
        Returns a Deck from the given deck page URL.
    """

    def __init__(self, driver: webdriver.Remote = None):
        self.logger = get_logger(self.log_filename, "MeleeScraper")
        super().__init__(driver=driver, logger=self.logger)

    ### Melee Public Functions

    def get_slots_from_event_url(self, url: str) -> namedtuple("EventSlots", ["total", "enrolled", "available"]):
        """
        Returns a namedtuple, EventSlots with attributes total, enrolled, and available.

        Parameters:
            url (str): The URL to an event.

        Returns:
            namedtuple(int, int, int): EventSlots(total, enrolled, available)
        """

        # Get page
        self._load(url)
        event_name = self._sanitized_title()
        self.logger.info(f"{url} - Processing event - {event_name}.")
        self.__accept_cookies()

        # Get tournament headline
        tournament_headline = (
            WebDriverWait(self.driver, LoadTime.STD)
            .until(EC.presence_of_element_located((By.XPATH, MeleeXPath.TOURNAMENT_HEADLINE)))
            .text
        )
        enrollment_info = tournament_headline.split("|")[-1]
        enrollment_nums = [int(i) for i in enrollment_info.split() if i.isdigit()]

        # Calculate event slot info
        EventSlots = namedtuple("EventSlots", ["total", "enrolled", "available"])
        event_slots = EventSlots(
            total=enrollment_nums[1],
            enrolled=enrollment_nums[0],
            available=enrollment_nums[1] - enrollment_nums[0],
        )
        return event_slots

    ### Public Function Overrides

    def get_decks_from_event_url(self, url: str, top8: bool = False) -> List[Deck]:
        # Get page
        self._load(url)
        event_name = self._sanitized_title()
        self.logger.info(f"{url} - Processing event - {event_name}.")
        self.__accept_cookies()

        if not top8:
            # Update the decklists per page to 500
            self.__set_per_page_max()
            self.__wait_for_standings()

        # Count the # of pages to scrape
        paginate_btns = WebDriverWait(self.driver, LoadTime.STD).until(
            EC.presence_of_all_elements_located((By.XPATH, MeleeXPath.PAGINATE_BTN))
        )
        page_count = int(paginate_btns[-1].get_attribute("textContent") if len(paginate_btns) > 1 else 1)

        # Process each page for this event
        deck_urls = []
        for p in range(1, page_count + 1):
            self.logger.debug(f"Processing page {p}/{page_count}.")
            deck_urls.extend(self.__get_deck_urls_from_pagination())

            # Top 8 only?
            if top8:
                break

            # Click to the next page
            next_page_btn = self.driver.find_element(By.ID, "tournament-standings-table_next")
            self.driver.execute_script("$(arguments[0]).trigger('click')", next_page_btn)
            self.__wait_for_standings()

        # TODO: This is a O(2n) way of doing this. If we could open a new window in get_deck_from_url, we could move
        # this to the above loop and do it in O(n). This operation is slow as it is.
        if top8:
            deck_urls = deck_urls[:8]
        decks = []
        for i in range(0, len(deck_urls)):
            print(f"Processing deck {i+1}/{len(deck_urls)}...", end="\r")
            decks.append(self.get_deck_from_url(deck_urls[i]))
        print()  # reset \r endline

        return decks

    def get_deck_from_url(self, url: str) -> Deck:
        # Get page
        self._load(url)
        deck_archetype = self._sanitized_title() or Deck.DEFAULT_ARCHETYPE
        self.logger.info(f"{url} - Processing deck - {deck_archetype}.")
        self.__accept_cookies()

        ## Get Deck parts
        # Format
        deck_format_element = WebDriverWait(self.driver, LoadTime.STD).until(
            EC.presence_of_element_located((By.XPATH, MeleeXPath.DECK_FORMAT))
        )
        deck_format = Format.get(deck_format_element.text)

        # Date
        date_played_element = WebDriverWait(self.driver, LoadTime.STD).until(
            EC.presence_of_element_located((By.XPATH, MeleeXPath.DATE_PLAYED))
        )
        date_played = datetime.strptime(date_played_element.text.strip(), Constants.MELEE_DATE_FORMAT)

        # Main and side
        main_elements = WebDriverWait(self.driver, LoadTime.STD).until(
            EC.presence_of_all_elements_located((By.XPATH, MeleeXPath.MAIN))
        )
        side_element = WebDriverWait(self.driver, LoadTime.STD).until(
            EC.presence_of_element_located((By.XPATH, MeleeXPath.SIDE))
        )

        # Create Deck
        deck = self._deck_from_parts(
            main_elements=main_elements,
            side_element=side_element,
        )
        deck.archetype = deck_archetype
        deck.date_played = date_played
        deck.format = deck_format

        return deck

    ### Protected Function Overrides

    def _sanitized_title(self) -> str:
        # NOTE: Melee decks and events are sanitized the same way.
        try:
            return self.driver.title.replace(" | Melee", "")
        except Exception as e:
            # raise(e)
            self.logger.warning(f"{self.driver.current_url} - Unable to sanitize title. Proceeding with defaults.")
            return ""

    def _deck_from_parts(self, main_elements: List[WebElement], side_element: WebElement) -> Deck:
        """
        Returns a Deck with the given main deck sections and sideboard WebElements.

        Parameters:
            main_elements (List[WebElement]): A list of WebElements containing main deck cards. Melee has type-based
            subsections.
            side_element (WebElement): A WebElement containing sideboard cards.

        Returns:
            deck (Deck): A Deck.
        """

        # Get the cards
        main_cards = Counter()
        for me in main_elements:
            main_cards.update(self._cards_from_element(me))
        side_cards = self._cards_from_element(side_element)

        # Create a Deck
        deck = Deck()
        deck.add_cards(cards=main_cards, in_the=InThe.MAIN)
        deck.add_cards(cards=side_cards, in_the=InThe.SIDE)

        return deck

    def _cards_from_element(self, deck_element: WebElement) -> List[Counter]:
        ## Get cards and quantities from the page
        quantities = [
            int(qe.get_attribute(MeleeXPath.QTY_DATA))  # WebElement containing quantity
            for qe in WebDriverWait(deck_element, LoadTime.STD).until(
                EC.presence_of_all_elements_located((By.XPATH, MeleeXPath.QTY))
            )
        ]
        card_names = [
            ce.get_attribute(MeleeXPath.CARD_DATA)  # WebElement containing card name
            for ce in WebDriverWait(deck_element, LoadTime.STD).until(
                EC.presence_of_all_elements_located((By.XPATH, MeleeXPath.CARD))
            )
        ]
        cards = dict(zip(card_names, quantities))

        return cards

    ### Melee Private Functions

    def __get_deck_urls_from_pagination(self) -> List[str]:
        """
        Returns a list of deck page URLs from the current WebDriver page.

        Returns:
            List[str]: A list of deck page URLs from the current WebDriver page.
        """

        # Grabs the URL for each decklist on the current page
        atags = WebDriverWait(self.driver, LoadTime.STD).until(
            EC.presence_of_all_elements_located((By.XPATH, MeleeXPath.DECK_URL))
        )
        deck_urls = [element.get_attribute("href") for element in atags]

        return deck_urls

    def __set_per_page_max(self) -> None:
        """
        Sets the decks-per-page to the maximum value. This will reduce the amount of pagination required to scrape all
        of the decklists from an event page.
        """

        # Find the option tag, set it to selected=true
        per_page_max_opt = WebDriverWait(self.driver, LoadTime.STD).until(
            EC.presence_of_element_located((By.XPATH, MeleeXPath.PER_PAGE_MAX_OPT))
        )
        self.driver.execute_script("arguments[0].setAttribute('selected', arguments[1])", per_page_max_opt, True)

        # Find the select tag, force it to update
        per_page_select = WebDriverWait(self.driver, LoadTime.STD).until(
            EC.presence_of_element_located((By.XPATH, MeleeXPath.PER_PAGE_SELECT))
        )
        self.driver.execute_script("$(arguments[0]).trigger('change')", per_page_select)

    def __wait_for_standings(self) -> None:
        """
        Waits for the Tournament Standings table to refresh before continuing to scrape decks.
        """

        # Wait until the tournament standings table is updated
        WebDriverWait(self.driver, LoadTime.LONG).until(
            EC.text_to_be_present_in_element_attribute((By.XPATH, MeleeXPath.PROCESSING_LBL), "style", "display: none")
        )

    def __accept_cookies(self) -> None:
        """
        Clicks the accept button for the request for cookies.
        """
        try:
            WebDriverWait(self.driver, LoadTime.STD).until(
                EC.presence_of_element_located((By.XPATH, MeleeXPath.ACCEPT_COOKIES_BTN))
            ).click()
            self.logger.info(f"Cookies accepted - {self.driver.current_url}")
        except TimeoutException as e:
            self.logger.info("Accept cookies button not found, skipping")
