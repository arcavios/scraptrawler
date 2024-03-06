import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from scooze.card import Card
from scooze.deck import Deck, DeckPart


# region Helper Functions

def get_html_document(url: str) -> str:
    """
    Extract HTML document form the given URL.
    """

    response = requests.get(url)

    return response.text

def get_apex_from_netloc(netloc: str) -> str:
    """
    Returns the apex domain from a given ParseResult.netloc
    """

    return netloc.split(".")[-2]

def deckpart_from_lines(lines: str) -> DeckPart:
    """
    TODO: docstring explaining how this takes N lines in the form <# card_name> and returns a DeckPart
    TODO: this will be slightly different between deck sites, so maybe add an enum for System to modify behavior
          for MDFCs, only Moxfield has the " // second_face_name"
    """

    part = DeckPart()

    for line in lines:
        quantity, card_name = line.split(" ", maxsplit=1)
        card = Card(name=card_name)
        part.add_card(card=card, quantity=int(quantity))

    return part

# endregion

def get_deck_from_url(url: str) -> Deck:
    """
    Generates a Deck from the given URL.

    Args:
        url: The url of the web page containing a decklist.

    Returns:
        A Deck representation of the dceklist at the given URL.
    """

    parse_result = urlparse(url)
    apex_domain = get_apex_from_netloc(parse_result.netloc)

    match(apex_domain):
        case "mtggoldfish":
            return get_deck_from_url_goldfish(url)
        case _:
            raise Exception("Invalid decklist URL.")


def get_deck_from_url_goldfish(url: str) -> Deck:
    deck_id = re.findall("\d{5,10}", url)

    # raise an exception if no deck ID is found in the URL
    if len(deck_id) > 0:
        deck_id = deck_id[0]
    else:
        raise Exception("MtgGoldfish: no deck ID found.")

    goldfish_target_url = f"https://www.mtggoldfish.com/deck/arena_download/{deck_id}"
    html = get_html_document(goldfish_target_url)
    soup = BeautifulSoup(html, 'html.parser')

    copy_paste_box_text = soup.find('textarea', {'class': 'copy-paste-box'}).text.strip()
    print(copy_paste_box_text)

    deck = Deck()
    deck_parts = copy_paste_box_text.split("\n\n")
    for part in deck_parts:
        lines = part.split("\n")
        match(lines[0]):
            case "Deck":
                main = deckpart_from_lines(lines[1:])
                deck.main = main
            case "Sideboard":
                side = deckpart_from_lines(lines[1:])
                deck.side = side
            case _:
                # TODO: logging
                print("MtgGoldfish: unknown decklist section found - " + lines[0])

    return deck
