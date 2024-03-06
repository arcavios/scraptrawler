import glob
import json
import os.path
from collections import Counter, namedtuple
from typing import Dict, List, Set

import requests

from scraptrawler.deck import Deck
from scraptrawler.scraper.melee import MeleeScraper
from scraptrawler.scraper.mtgo import MtgoScraper
from scraptrawler.utils import DecklistFormatter

##########
### Think of this file as a scratch pad. It should always run when you commit your code, but it doesn't need to
### be beatiful. Eventually it will get deleted and replaced by real test cases, but this is a useful tool to have
### so you don't have to constantly use Python IDLE or something.
##########


## Debug Flags
DEBUG = True
ONLY_TOP_8 = True

# Melee
DO_MELEE_ENROLLMENT = True
DO_MELEE = True

# Mtgo
DO_MTGO = True

# Unused
DO_COUNT_CARDS = False
DO_FILTER_CARDS = False

## Constants
DATA_PATH = "./data"


# TODO: docstring
def main():
    ## Clean out data dir
    files = glob.glob(f"{DATA_PATH}/*.txt", recursive=True)

    for f in files:
        try:
            os.remove(f)
        except OSError as e:
            print("Error: %s : %s" % (f, e.strerror))

    ### Test Melee Scraper

    melee_event_urls = []
    melee_deck_url = "https://melee.gg/Decklist/View/290170"
    if DEBUG:
        # melee_event_urls = ["https://melee.gg/Tournament/View/16910"]  # small event to test with
        melee_event_urls = ["https://melee.gg/Tournament/View/15367"]
    else:
        melee_event_urls = [  # List of all RC events
            "https://melee.gg/Tournament/View/15367",  # Dreamhack Dallas '23
            "https://melee.gg/Tournament/View/15656",  # MTG SEA Championship Final Cycle 3
            "https://melee.gg/Tournament/View/15616",  # MTC China Open S3 Regional Championship
            "https://melee.gg/Tournament/View/15170",  # F2F Tour Championship - Toronto Round 3
            "https://melee.gg/Tournament/View/15498",  # The Gathering Showdown Series
            "https://melee.gg/Tournament/View/15288",  # Legacy European Championship Athens
            "https://melee.gg/Tournament/View/15416",  # MIT Championship
            "https://melee.gg/Tournament/View/15169",  # F2F Tour Championship -Edmonton Round 3
            "https://melee.gg/Tournament/View/15397",  # Champions Cup Final Cycle 3
            "https://melee.gg/Tournament/View/15524",  # City Class Games Showdown III
            "https://melee.gg/Tournament/View/15828",  # South America Magic Series
        ]

    melee_scraper = MeleeScraper()
    melee_event_enrollments: List[namedtuple] = []
    melee_decks: List[Deck] = []

    ## Run selenium and chromedriver to scrape data from MTG Melee for each event
    melee_decks.append(melee_scraper.get_deck_from_url(url=melee_deck_url))
    for event_url in melee_event_urls:
        if DO_MELEE_ENROLLMENT:
            melee_event_enrollments.append(melee_scraper.get_slots_from_event_url(url=event_url))

        if DO_MELEE:
            melee_decks.extend(melee_scraper.get_decks_from_event_url(url=event_url, top8=ONLY_TOP_8))

    # Test get_slots_from_event_url
    if DO_MELEE_ENROLLMENT:
        for event_slots in melee_event_enrollments:
            print(
                f"{event_slots.available} slots available. {event_slots.enrolled} players enrolled. {event_slots.total} total slots."
            )
    else:
        print("Please set DO_MELEE_ENROLLMENT to test get_slots_from_event_url...")

    # TODO: If you want to get some sample data, consider writing this to a file
    if DO_MELEE:
        for deck in melee_decks:
            with open(f"{DATA_PATH}/decks.json", "a") as f:
                f.write(deck.to_json() + "\n")
            print(deck.to_json())
            print("---------------")
    else:
        print("Please set DO_MELEE to test the deck scraper...")

    ### Test MTGO Scraper
    mtgo_event_urls = []
    if DEBUG:
        mtgo_deck_url = "https://www.mtgo.com/en/mtgo/decklist/modern-preliminary-2023-07-2012568051#deck_DInglis"  # Specific Player Deck URL
        mtgo_event_urls = [
            "https://www.mtgo.com/en/mtgo/decklist/modern-preliminary-2023-07-1912568044"
        ]  # July 19, 2023 - Modern Prelim

    else:
        mtgo_event_urls = [  # List of all July 8 Challenge events
            "https://www.mtgo.com/en/mtgo/decklist/pauper-challenge-2023-07-0812564209",  # July 8, 2023 - Pauper Challenge
            "https://www.mtgo.com/en/mtgo/decklist/standard-challenge-32-2023-07-0812564211",  # July 8, 2023 - Standard Challenge
            "https://www.mtgo.com/en/mtgo/decklist/pioneer-challenge-2023-07-0812564215",  # July 8, 2023 - Pioneer Challenge
            "https://www.mtgo.com/en/mtgo/decklist/modern-challenge-2023-07-0812564212",  # July 8, 2023 - Modern Challenge
            "https://www.mtgo.com/en/mtgo/decklist/legacy-challenge-32-2023-07-0812564210",  # July 8, 2023 - Legacy Challenge
            "https://www.mtgo.com/en/mtgo/decklist/vintage-challenge-2023-07-0812564213",  # July 8, 2023 - Vintage Challenge
        ]

    mtgo_scraper = MtgoScraper()
    mtgo_decks: List[Deck] = []

    ## Run selenium and chromedriver to scrape data from MTG Melee for each event
    mtgo_decks.append(mtgo_scraper.get_deck_from_url(mtgo_deck_url))
    for event_url in mtgo_event_urls:
        if DO_MTGO:
            mtgo_decks.extend(mtgo_scraper.get_decks_from_event_url(url=event_url, top8=ONLY_TOP_8))

    # TODO: If you want to get some sample data, consider writing this to a file
    if DO_MTGO:
        for deck in mtgo_decks:
            # with open(f"{DATA_PATH}/decks.txt", "a") as f:
            #     f.write(deck.to_json())
            print(deck.to_json())
            # print(deck.to_decklist("not a format lol"))
            # print(deck.to_decklist(DecklistFormat.ARENA))
            print("---------------")
    else:
        print("Please set DO_MTGO to test the deck scraper...")

    # Write deck URLs to a file
    # if DO_SCRAPE:
    #     print("Writing deck URLs to file deck_urls.txt...")
    #     with open(f"{DATA_PATH}/deck_urls.txt", "w") as f:
    #         f.write("\n".join(deck_urls))

    # Count the total cards in all event decklists
    # if DO_COUNT_CARDS:
    #     # If we didn't scrape, we need to read the deck URLs from a file
    #     if not DO_SCRAPE:
    #         deck_urls = []
    #         print("Loading deck urls from deck_urls.txt...")
    #         with open(f"{DATA_PATH}/deck_urls.txt", "r") as f:
    #             for deck_url in f.readlines():
    #                 deck_urls.append(deck_url.strip())

    #     # Count total cards
    #     total_cards = total_cards_from_urls(scraper=scraper, deck_urls=deck_urls)
    #     print("Writing cards to file total_cards.txt...")
    #     with open(f"{DATA_PATH}/total_cards.txt", "w") as f:
    #         f.write("\n".join(f"{q} {c}" for c, q in sorted(total_cards.items(), key=lambda item: (-item[1], item[0]))))
    # else:
    #     print("Please set DO_COUNT_CARDS to run the card counter...")

    # Filter cards available on Arena
    # if DO_FILTER_CARDS:
    #     # Read cards into total_cards
    #     total_cards = {}
    #     with open(f"{DATA_PATH}/total_cards.txt", "r") as f:
    #         for line in f.readlines():
    #             q, c = line.split(" ", maxsplit=1)
    #             total_cards[c.strip()] = int(q)

    #     # Filter non-Arena cards
    #     non_legal_cards = filter_cards_for_arena_nonlegal(total_cards)
    #     # print(non_legal_cards.items())
    #     print("Writing cards to file non_legal_cards.txt...")
    #     with open(f"{DATA_PATH}/non_legal_cards.txt", "w") as f:
    #         f.write(
    #             "\n".join(f"{q} {c}" for c, q in sorted(non_legal_cards.items(), key=lambda item: (-item[1], item[0])))
    #         )
    # else:
    #     print("Please set DO_FILTER_CARDS to run the card counter...")

    ## Clean up
    melee_scraper.driver.quit()
    mtgo_scraper.driver.quit()


# TODO: move to scraper
# def total_cards_from_urls(scraper: Scraper, deck_urls: List[str]) -> Dict[str, int]:
#     total_cards = Counter()
#     deck_count = len(deck_urls)
#     for i in range(0, deck_count):
#         deck_url = deck_urls[i]
#         print(f"Processing deck {i+1}/{deck_count}", end="\r")
#         try:
#             total_cards.update(scraper.deck_from_url(deck_url))
#         except Exception as e:
#             print(f"\nError encountered while processing deck_url {deck_url}. Exception: {str(e)}")
#     print()
#     return total_cards


# TODO: move to deck or scraper? or use ophidian import?
def explorer_legal_cards() -> Set[str]:
    cards = set()
    with open(f"{DATA_PATH}/explorer_legal_cards.txt", "r") as f:
        for card in f.readlines():
            cards.add(card.strip())
    return cards


# TODO: move to deck or scraper? or use ophidian import?
def filter_cards_for_arena_nonlegal(card_list: Dict[str, int]) -> Dict[str, int]:
    explorer_cards = explorer_legal_cards()
    nonlegal_cards = {}
    for name, q in card_list.items():
        if name not in explorer_cards:
            nonlegal_cards[name] = q
    return nonlegal_cards


if __name__ == "__main__":
    main()
