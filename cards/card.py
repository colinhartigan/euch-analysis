
SUIT_ICONS = {2: "♡", 4: "♦", 3: "♣", 1: "♠"}
RANKS = {
    7: "7",
    8: "8",
    9: "9",
    10: "10",
    11: "j",
    12: "q",
    13: "k",
    14: "a",
}
SUITS = {
    1: "spades",
    2: "hearts",
    3: "clubs",
    4: "diamonds"
}
RANK_PRETTY = {
    7: "7",
    8: "8",
    9: "9",
    10: "10",
    11: "J",
    12: "Q",
    13: "K",
    14: "A"
}


def get_suit_id(suit: str) -> int:
    return SUITS[suit.upper()]


def get_suit_name(suit_id: int) -> str:
    for key, value in SUITS.items():
        if value == suit_id:
            return key
    return None


class Card:
    def __init__(self, rank: int, suit: int):
        self._rank: int = rank
        self._suit: int = suit

    def __repr__(self) -> str:
        return f"{SUIT_ICONS[self.suit]}{RANK_PRETTY[self.rank]}"

    @property
    def rank(self) -> int:
        return self._rank

    @property
    def suit(self) -> int:
        return self._suit
