import logging
from enum import IntEnum
from typing import Counter, List

import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from scraptrawler.deck import Deck, InThe
from scraptrawler.utils import ExtendedEnum, get_logger


class LoadTime(ExtendedEnum, IntEnum):
    """
    A class used for standardized load times to be used during WebDriverWait.

    Attributes
    ----------
    STD (5) : Standard load time for interacting with normal DOM elements.
    LONG (10) : Long load time while waiting for AJAX or other non-standard elements.
    """

    STD = 5
    LONG = 10


class BaseScraper:
    """
    A class to represent a web scraper used to get data about
    Magic: the Gathering decklists and results.

    Attributes
    ----------
    driver : webdriver.Remote
        Controls a browser by sending commands to a remote server.

    Methods
    -------
    get_decks_from_event_url(url: str, top8: bool):
        Returns a list of Decks from the given event URL.
    get_deck_from_url(url: str):
        Returns a Deck from the given deck page URL.
    """

    ## Class Attributes
    log_filename = "scraper.log"

    def __init__(
        self,
        driver: webdriver.Remote = None,
        logger: logging.Logger = get_logger(log_filename, "BaseScraper"),
    ):
        self.driver = driver
        self.logger = logger
        self.__post_init__()

    def __post_init__(self):
        if self.driver is None:
            ## Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--headless=new")  # Ensure GUI is off

            # Setup Chrome service
            # NOTE: ChromeDriverManager(driver_version="") refers to the local google-chrome --version
            # NOTE: There is a bug if you have a Chrome version that is too new with no matching chromedriver
            chrome_service = Service(ChromeDriverManager().install())

            # Choose Chrome Browser
            self.driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
            self.driver.maximize_window()

    ### Public Functions

    def get_decks_from_event_url(self, url: str) -> List[Deck]:
        """
        Returns a list of Decks from the given event URL.

        Parameters:
            url (str): The URL to an event.
            top8 (bool): Return only the top 8 Decks, default = False.

        Returns:
            List[Deck]: A list of Decks from the given event URL.
        """
        raise (NotImplementedError)

    def get_deck_from_url(self, url: str) -> Deck:
        """
        Returns a Deck from the given URL.

        Parameters:
            url (str): The URL to a deck.

        Returns:
            deck (Deck): A dict of the cards in the given deck.
        """
        raise (NotImplementedError)

    ### Protected Functions

    def _load(self, url: str) -> None:
        """
        Tries to load a web page in the current browser session.

        Parameters:
            url (str): The URL to a web page (generally an event or decklist page).
        """
        try:
            r = requests.get(url)
            self.logger.debug(f"URL status - URL: {url}, Status: {r.status_code}")
        except requests.exceptions.RequestException as e:
            self.logger.error(e)
            raise SystemExit(e)
        else:
            self.driver.get(url)

    def _sanitized_title(self) -> str:
        """
        Provides a plain-text version of the current web page title.
        Use _load(url) before executing this function.

        Returns:
            title (str): A sanitized title.
        """
        raise (NotImplementedError)

    def _decks_from_elements(self, main_elements: List[WebElement], side_elements: List[WebElement]) -> List[Deck]:
        """
        Returns a list of Decks from the given WebElements.

        Parameters:
            main_elements (List[WebElement]): The WebElements containing main deck cards.
            side_elements (List[WebElement]): The WebElements containing sideboard cards.

        Returns:
            decks (List[Deck]): A list of decks.
        """
        raise (NotImplementedError)

    def _deck_from_parts(self, main_element: WebElement, side_element: WebElement) -> Deck:
        """
        Returns a Deck with the given main deck and sideboard WebElements.

        Parameters:
            main_element (WebElement): A WebElement containing main deck cards.
            side_element (WebElement): A WebElement containing sideboard cards.

        Returns:
            deck (Deck): A Deck.
        """
        raise (NotImplementedError)

    def _cards_from_element(self, deck_element: WebElement) -> List[Counter]:
        """
        Returns a List of cards in the given deck element

        Parameters:
            deck_element (WebElement): A WebElement containing cards.

        Returns:
            cards (List[Counter[str]]): A list of cards.
        """
        raise (NotImplementedError)
