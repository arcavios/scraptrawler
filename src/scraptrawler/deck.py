import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
from enum import auto
from typing import Dict

from ftfy import fix_encoding
from scraptrawler.utils import DecklistFormatter, ExtendedEnum, get_logger
from strenum import StrEnum


class InThe(ExtendedEnum, StrEnum):
    """
    The location of a card in a deck.

    Attributes
    ----------
    MAIN: Main deck
    SIDE: Sideboard
    """

    MAIN = auto()
    SIDE = auto()


class Format(ExtendedEnum, StrEnum):
    """
    The format a deck was played in.

    Attributes
    ----------
    VINTAGE: Vintage
    LEGACY: Legacy
    PAUPER: Pauper
    MODERN: Modern
    PIONEER: Pioneer
    STANDARD: Standard
    """

    VINTAGE = "Vintage"
    LEGACY = "Legacy"
    PAUPER = "Pauper"
    MODERN = "Modern"
    PIONEER = "Pioneer"
    STANDARD = "Standard"


class Deck:
    """
    A class to represent a deck of Magic: the Gathering cards.

    Attributes
    ----------
    archetype : str
        The archetype of this deck.
    format : Deck.Format
        The format of the event this deck was played in.
    date_played : datetime
        The date this deck was played.
    main : dict[str:int]
        The main deck (generally 60 cards).
    side : dict[str:int]
        The sideboard (generally 15 cards).

    Methods
    -------
    add_card(card: str, quantity: int, in_the: InThe):
        Adds a given quantity of a given card to this Deck.
    add_cards(cards: Dict[str, int], in_the: InThe):
        Adds the given cards to this Deck.
    as_cards():
        Returns all the cards in this Deck as a dict[str:int]
    count_main():
        Counts the cards in the main deck.
    count_side():
        Counts the cards in the sideboard.
    count_all():
        Counts all of the cards in this Deck.
    to_json():
        Converts this Deck to JSON.
    to_decklist(DecklistFormat):
        Exports the Deck as a str with the given DecklistFormat.
    """

    ## Class Attributes
    # Set up logger
    log_filename = "deck.log"
    logger = get_logger(log_filename, "deck")

    # Constants
    DEFAULT_ARCHETYPE = ""

    def __init__(
        self,
        archetype: str = DEFAULT_ARCHETYPE,
        format: Format = None,
        date_played: datetime = datetime.today(),
        main: Counter = Counter(),
        side: Counter = Counter(),
    ):
        self.archetype = archetype
        self.date_played = date_played
        self.format = format

        # Deep copy of main and side
        self.main, self.side = Counter(), Counter()
        self.main.update(main)
        self.side.update(side)

    def __eq__(self, other):
        return (
            self.archetype == other.archetype
            and self.date_played == other.date_played
            and self.format == other.format
            and self.main == other.main
            and self.side == other.side
        )

    def add_cards(self, cards: Dict[str, int], in_the: InThe = InThe.MAIN) -> None:
        """
        Adds the given cards to this Deck.

        Parameters:
            cards Dict[str:int]: The cards to add.
            in_the (InThe): Where to add the cards (main, side, etc)
        """
        for c, q in cards.items():
            self.add_card(card=c, quantity=q, in_the=in_the)

    def add_card(self, card: str, quantity: int = 1, in_the: InThe = InThe.MAIN) -> None:
        """
        Adds a given quantity of a given card to this Deck.

        Parameters:
            card (str): The card to add.
            quantity (int): The number of copies of the card to be added.
            in_the (InThe): Where to add the card (main, side, etc)
        """
        card = fix_encoding(card)  # Fixes UTF-8 encoding issues like "3 LÃ³rien Revealed" -> "3 Lórien Revealed"
        match in_the:
            case InThe.MAIN:
                self.main.update({card: quantity})
                self.logger.debug(f"{self.archetype} - Added {quantity} copies of {card} to the main deck.")
            case InThe.SIDE:
                self.side.update({card: quantity})
                self.logger.debug(f"{self.archetype} - Added {quantity} copies of {card} to the sideboard.")
            case _:
                self.logger.error(
                    f"{self.archetype} - Unable to add {quantity} copies of {card} to the deck. 'in' must be one of {InThe.list()}"
                )

    def as_cards(self) -> Counter:
        """
        Returns a Counter containing all the cards in this deck. Combines main and side.

        Returns:
            cards (dict[str: int]): A dict with card names and quantities from main and side combined.
        """
        cards = Counter()
        cards.update(self.main)
        cards.update(self.side)
        return cards

    def count_main(self) -> int:
        """
        Returns:
            int: The number of cards in this Deck's main.
        """
        return len(self.main)

    def count_side(self) -> int:
        """
        Returns:
            int: The number of cards in this Deck's side.
        """
        return len(self.side)

    def count_all(self) -> int:
        """
        Returns:
            int: The number of cards in this Deck.
        """
        return self.count_main() + self.count_side()

    def to_json(self) -> str:
        """
        Returns:
            dict: A JSON object with the data stored in this Deck.
        """
        return json.dumps(self.__dict__, indent=4, ensure_ascii=False, default=str)

    def to_decklist(self, decklist_formatter: DecklistFormatter = None) -> str:
        """
        Exports this Deck as a str with the given DecklistFormatter.

        Parameters:
            export_format (DecklistFormatter): The format of the exported Deck.

        Returns:
            decklist (str): A string containing the names and quantities of the cards in this Deck.
        """

        match decklist_formatter:
            case DecklistFormatter.ARENA:
                sb_prefix = "Sideboard\n"
                # TODO: filter out cards that are not on Arena. Log a WARNING with those cards.
                self.logger.debug(f"{self.archetype} - Exporting for Arena.")
            case DecklistFormatter.MTGO:
                sb_prefix = "SIDEBOARD:\n"
                # TODO: filter out cards that are not on MTGO. Log a WARNING with those cards.
                self.logger.debug(f"{self.archetype} - Exporting for MTGO.")
            case _:
                sb_prefix = ""  # Default
                self.logger.warning(
                    f"""{self.archetype} - Unable to export with the given format: {decklist_formatter}. """
                    f"""'export_format' must be one of {DecklistFormatter.list()}. Using default format."""
                )
        sb_prefix = "\n\n" + sb_prefix

        # Build the decklist string
        main = "\n".join([f"{quantity} {card_name}" for card_name, quantity in self.main.items()])
        side = sb_prefix + "\n".join([f"{quantity} {card_name}" for card_name, quantity in self.side.items()])
        decklist = f"{main}{side if self.count_side() > 0 else ''}"
        return decklist
