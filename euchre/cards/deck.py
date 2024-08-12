import random

from .card import RANKS, SUITS, Card


class Deck:

    def __init__(self):
        self.cards: list[Card] = []

        self.build()

    def build(self):
        for suit in SUITS.keys():
            for rank in RANKS.keys():
                self.cards.append(Card(rank, suit))
            self.shuffle()

    def add(self, card: Card):
        self.cards.append(card)

    def shuffle(self):
        random.shuffle(self.cards)

    def draw(self) -> Card:
        return self.cards.pop()

    def deal(self, n: int) -> list[Card]:
        return [self.draw() for _ in range(n)]
