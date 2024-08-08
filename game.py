import random

import pydealer as pd

SUITS = {
    "Spades": 1,
    "Hearts": 2,
    "Clubs": 3,
    "Diamonds": 4
}
DEFAULT_RANKS = {
    "values": {
        "Ace": 14,
        "King": 13,
        "Queen": 12,
        "Jack": 11,
        "10": 10,
        "9": 9,
        "8": 8,
        "7": 7,
    },
    "suits": {
        "Spades": 1,
        "Hearts": 1,
        "Clubs": 1,
        "Diamonds": 1
    }
}


class Player:
    def __init__(self, p_id, t_id):
        self.id = p_id
        self.team = t_id
        self.hand = pd.Stack()

    def __repr__(self) -> str:
        return f"player {self.id} (team {self.team.t_id})"

    def turn(self, trump: int, pile: pd.Stack) -> pd.Card:
        pass

    def prompt_trump(self, flop: pd.Card) -> bool:
        return random.choice([True, False])

    def call_trump(self) -> str:
        return random.choice(["Spades", "Hearts", "Clubs", "Diamonds"])

    def prompt_discard(self, flop: pd.Card) -> pd.Card:
        return random.choice(self.hand)


class Team:
    def __init__(self, t_id):
        self.t_id = t_id
        self.score = 0


class Game:
    def __init__(self):
        self.players = []
        self.teams = [Team(i) for i in range(2)]
        self.dealer_id = 0

        self.rounds = []

        self.players = [Player(p_id=i, t_id=self.teams[i % 2])
                        for i in range(4)]

    def play_game(self):
        dealer_id = 0
        while any([team.score < 10 for team in self.teams]):
            self.play_round(dealer_id)
            dealer_id += 1
            dealer_id %= 4

    def play_round(self, dealer_id):
        current_round = Round(self.players, self.players[self.dealer_id])
        current_round.play_round()


class Round:

    players: list[Player]
    dealer: Player
    player_order: list[Player]
    trump: str
    deck: pd.Deck

    def __init__(self, players: list[Player], dealer: Player):
        self.tricks = []
        self.dealer = dealer
        self.players = players
        self.player_order = []
        self.trump = None
        self.deck = pd.Deck(cards=[pd.Card(value=v, suit=s)
                            for v in DEFAULT_RANKS["values"].keys() for s in DEFAULT_RANKS["suits"].keys()], build=False)

        self.deck.shuffle()

    def play_round(self):
        # deal cards to players
        for player in [self.players[(self.dealer.id + i) % 4] for i in range(4)]:
            player.hand = self.deck.deal(5)

        leader_id = 0

        # trump selection
        flop = self.deck.deal(1)[0]
        for player in [self.players[(self.dealer.id + i + 1) % 4] for i in range(4)]:
            if player.prompt_trump(flop):
                print(f"player {player.id} picked up trump ({flop})")
                self.trump = flop.suit
                discarded = player.prompt_discard(flop)
                if not discarded in player.hand:
                    raise ValueError("player discarded card not in hand")

                for i, card in enumerate(player.hand):
                    if card == discarded:
                        del player.hand[i]
                        break

                self.deck.add(discarded)
                player.hand.add(flop)
                leader_id = player.id
                break

        if not self.trump:
            for player in [self.players[(self.dealer.id + i + 1) % 4] for i in range(4)]:
                if called_suit := player.call_trump():
                    print(f"player {player.id} called trump ({flop})")
                    self.trump = called_suit
                    leader_id = player.id
                    break

        print(f"trump: {self.trump}")

        player_order = [self.players[(leader_id + i) % 4] for i in range(4)]

        for i in range(5):
            trick = Trick(player_order, self.trump)
            trick.play_trick()


class Trick:
    def __init__(self, players: list[Player], trump: pd.Card):
        self.pile = pd.Stack()
        self.players = players
        self.trump = trump

    def judge_leader(self):
        pass

    def play_trick(self):
        for player in self.players:
            played_card = player.turn(self.trump, self.pile)
            self.pile.add((played_card, player))

            if not played_card in player.hand:
                raise ValueError("player discarded card not in hand")

            print(f"player {player.id} played {played_card}")

            for i, card in enumerate(player.hand):
                if card == played_card:
                    del player.hand[i]
                    break

            self.judge_leader(self.pile)


if __name__ == "__main__":
    game = Game()
    game.play_game()
