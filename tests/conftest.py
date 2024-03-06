from collections import Counter

import pytest
from scooze.card import Card
from scooze.deck import Deck, DeckPart

# region Heroic Cards and Deck

# region Cards


@pytest.fixture(scope="session")
def adanto_vanguard() -> Card:
    return Card(name="Adanto Vanguard")


@pytest.fixture(scope="session")
def ancestral_anger() -> Card:
    return Card(name="Ancestral Anger")


@pytest.fixture(scope="session")
def battlefield_forge() -> Card:
    return Card(name="Battlefield Forge")


@pytest.fixture(scope="session")
def defiant_strike() -> Card:
    return Card(name="Defiant Strike")


@pytest.fixture(scope="session")
def destroy_evil() -> Card:
    return Card(name="Destroy Evil")


@pytest.fixture(scope="session")
def dreadhorde_arcanist() -> Card:
    return Card(name="Dreadhorde Arcanist")


@pytest.fixture(scope="session")
def eiganjo_seat_of_the_empire() -> Card:
    return Card(name="Eiganjo, Seat of the Empire")


@pytest.fixture(scope="session")
def favored_hoplite() -> Card:
    return Card(name="Favored Hoplite")


@pytest.fixture(scope="session")
def flowstone_infusion() -> Card:
    return Card(name="Flowstone Infusion")


@pytest.fixture(scope="session")
def gods_willing() -> Card:
    return Card(name="Gods Willing")


@pytest.fixture(scope="session")
def homestead_courage() -> Card:
    return Card(name="Homestead Courage")


@pytest.fixture(scope="session")
def illuminator_virtuoso() -> Card:
    return Card(name="Illuminator Virtuoso")


@pytest.fixture(scope="session")
def inspiring_vantage() -> Card:
    return Card(name="Inspiring Vantage")


@pytest.fixture(scope="session")
def invigorated_rampage() -> Card:
    return Card(name="Invigorated Rampage")


@pytest.fixture(scope="session")
def jegantha_the_wellspring() -> Card:
    return Card(name="Jegantha, the Wellspring")


@pytest.fixture(scope="session")
def lorans_escape() -> Card:
    return Card(name="Loran's Escape")


@pytest.fixture(scope="session")
def monastery_swiftspear() -> Card:
    return Card(name="Monastery Swiftspear")


@pytest.fixture(scope="session")
def needleverge_pathway() -> Card:
    return Card(name="Needleverge Pathway")


@pytest.fixture(scope="session")
def plains() -> Card:
    return Card(name="Plains")


@pytest.fixture(scope="session")
def reckless_rage() -> Card:
    return Card(name="Reckless Rage")


@pytest.fixture(scope="session")
def reidane_god_of_the_worthy() -> Card:
    return Card(name="Reidane, God of the Worthy")


@pytest.fixture(scope="session")
def rending_volley() -> Card:
    return Card(name="Rending Volley")


@pytest.fixture(scope="session")
def sacred_foundry() -> Card:
    return Card(name="Sacred Foundry")


@pytest.fixture(scope="session")
def sejiri_shelter() -> Card:
    return Card(name="Sejiri Shelter")


@pytest.fixture(scope="session")
def spikefield_hazard() -> Card:
    return Card(name="Spikefield Hazard")


@pytest.fixture(scope="session")
def steel_seraph() -> Card:
    return Card(name="Steel Seraph")


@pytest.fixture(scope="session")
def heroic_main(
    adanto_vanguard,
    ancestral_anger,
    battlefield_forge,
    defiant_strike,
    dreadhorde_arcanist,
    eiganjo_seat_of_the_empire,
    favored_hoplite,
    flowstone_infusion,
    gods_willing,
    homestead_courage,
    illuminator_virtuoso,
    inspiring_vantage,
    invigorated_rampage,
    monastery_swiftspear,
    needleverge_pathway,
    plains,
    reckless_rage,
    sacred_foundry,
    sejiri_shelter,
    spikefield_hazard,
) -> DeckPart:
    cards = Counter(
        {
            adanto_vanguard: 2,
            ancestral_anger: 4,
            battlefield_forge: 4,
            defiant_strike: 4,
            dreadhorde_arcanist: 4,
            eiganjo_seat_of_the_empire: 1,
            favored_hoplite: 4,
            flowstone_infusion: 2,
            gods_willing: 4,
            homestead_courage: 3,
            illuminator_virtuoso: 4,
            inspiring_vantage: 4,
            invigorated_rampage: 2,
            monastery_swiftspear: 4,
            needleverge_pathway: 4,
            plains: 1,
            reckless_rage: 3,
            sacred_foundry: 4,
            sejiri_shelter: 1,
            spikefield_hazard: 1,
        }
    )

    return DeckPart(cards)


@pytest.fixture(scope="session")
def heroic_side(
    destroy_evil,
    jegantha_the_wellspring,
    lorans_escape,
    reckless_rage,
    reidane_god_of_the_worthy,
    rending_volley,
    steel_seraph,
) -> DeckPart:
    cards = Counter(
        {
            destroy_evil: 2,
            jegantha_the_wellspring: 1,
            lorans_escape: 2,
            reckless_rage: 1,
            reidane_god_of_the_worthy: 2,
            rending_volley: 3,
            steel_seraph: 4,
        }
    )

    return DeckPart(cards)


# endregion


@pytest.fixture(scope="session")
def deck_pioneer_heroic(heroic_main, heroic_side) -> Deck:
    return Deck(archetype="Boros Heroic", main=heroic_main, side=heroic_side)


# endregion
