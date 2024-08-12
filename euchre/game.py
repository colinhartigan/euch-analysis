import random

from cards.card import COMPLEMENTARY_SUITS, SUIT_ICONS, SUITS, Card
from cards.deck import Deck


class Player:
    def __init__(self, p_id, t_id):
        self.id = p_id
        self.team = t_id
        self.hand: list[Card] = []

    def __repr__(self) -> str:
        return f"player {self.id} (team {self.team.t_id})"

    def turn(self, trump_suit: int, lead_suit: int, pile: list[Card]) -> Card:
        if not lead_suit:
            return random.choice(self.hand)

        else:
            for card in self.hand:
                if card.effective_suit == lead_suit:
                    return card
            return random.choice(self.hand)

    def prompt_trump(self, flop: Card) -> bool:
        return random.choice([True, False])

    def call_trump(self) -> str:
        return random.choice(list(SUITS.keys()))
    
    def go_alone(self) -> bool:
        return False

    def prompt_discard(self, flop: Card) -> Card:
        return random.choice(self.hand)


class Team:
    def __init__(self, t_id):
        self.t_id = t_id
        self.score = 0

    def __repr__(self) -> str:
        return f"team {self.t_id} ({self.score} points)"


class Game:
    def __init__(self):
        self.teams: list[Team] = [Team(i) for i in range(2)]
        self.players: list[Player] = [Player(p_id=i, t_id=self.teams[i % 2]) for i in range(4)]
        self.dealer_id = 0

        self.rounds = []

    def play_game(self):
        dealer_id = 0
        while any([team.score < 10 for team in self.teams]):
            self.play_round(dealer_id)
            dealer_id += 1
            dealer_id %= 4

    def play_round(self, dealer_id):
        current_round = Round(self.players, self.players[dealer_id])
        current_round.play_round()


class Round:

    def __init__(self, players: list[Player], dealer: Player):
        self.tricks: list[tuple[Player, list[tuple[Player, Card]]]] = []
        self.dealer: Player = dealer
        self.players: list[Player] = players
        self.player_order: list[Player] = []
        self.trump_suit: int = None
        self.deck: Deck = Deck()

        print("\n\n--- new round ---\n")
        print(f"starting round with dealer {dealer.id}")

    def play_round(self):
        # deal cards to players
        for player in [self.players[(self.dealer.id + i) % 4] for i in range(4)]:
            player.hand = self.deck.deal(5)

        caller: Player = None

        # trump selection
        flop = self.deck.draw()
        call_order: list[Player] = [
            self.players[(self.dealer.id + i + 1) % 4] for i in range(4)]
        for player in call_order:
            if player.prompt_trump(flop):
                self.trump_suit = flop.suit
                discarded = player.prompt_discard(flop)
                print(f"player {player.id} picked up trump ({
                      flop}) and discarded {discarded}")
                if not discarded in player.hand:
                    raise ValueError("player discarded card not in hand")

                for card in player.hand:
                    if card == discarded:
                        player.hand.remove(card)
                        break

                self.deck.add(discarded)
                player.hand.append(flop)
                caller = player                    

                break
            else:
                print(f"player {player.id} passed")

        if not self.trump_suit:
            for player in call_order:
                if called_suit := player.call_trump():
                    print(f"player {player.id} called trump (flop was {flop})")
                    self.trump_suit = called_suit
                    caller = player
                    break

        if caller.go_alone():
            print(f"player {caller.id} is going alone")
            call_order = [i for i in call_order if i != caller]

        print(f"trump: {SUIT_ICONS[self.trump_suit]}\n")

        # check if anyone is holding the left bower and update its effective suit
        for player in self.players:
            for card in player.hand:
                if card.suit == COMPLEMENTARY_SUITS[self.trump_suit] and card.rank == 11:
                    card._effective_suit = self.trump_suit

        for i in range(5):
            trick = Trick(call_order, self.trump_suit)
            winner, pile = trick.play_trick()

            self.tricks.append((winner, pile))

            # evaluate scores
            scores: dict[Team, list[tuple[Player, Card]]] = {}
            for winner, pile in self.tricks:
                scores[winner.team] = scores.get(winner.team, 0) + 1

            print("\n".join([f"{team}: {score}" for team, score in scores.items()]))

            round_end = False

            for team in scores.keys():
                if team == self.players[caller.id].team:
                    if scores[team] == 5:
                        team.score += 2
                        print(f"calling team won 5 tricks, +2")
                        round_end = True
                    elif scores[team] >= 3:
                        team.score += 1
                        round_end = True
                        print(f"calling team won 3 tricks, +1")
                else:
                    if scores[team] >= 3:
                        team.score += 2
                        round_end = True
                        print(f"EUCHRE! defending team won 3 tricks, +2")

            if round_end:
                print("round over")
                break



class Trick:
    def __init__(self, players: list[Player], trump: int):
        self.pile: list[tuple[Player, Card]] = []
        self.players: list[Player] = players
        self.trump_suit: int = trump

        self.lead_suit: int = None

    def judge_leader(self) -> tuple[Player, str]:
        leader = self.pile[0] 

        suit_ranks = {
            self.trump_suit: 2,
            self.lead_suit: 1,
        }
        unused_suits = [suit for suit in SUITS.keys() if suit not in suit_ranks.keys()]
        suit_ranks.update({suit: 0 for suit in unused_suits})


        for player, card in self.pile[1:]:
            # jack of trump is best
            if card.suit == self.trump_suit and card.rank == 11:
                leader = (player, card)
                break

            # next best is jack of same color as trump suit
            elif card.effective_suit == self.trump_suit and card.rank == 11:
                leader = (player, card)

            # check if leader is a bower
            if leader[1].effective_suit == self.trump_suit and leader[1].rank == 11:
                continue
            # then high trump
            elif suit_ranks[card.suit] > suit_ranks[leader[1].suit]:
                leader = (player, card)

            # then high lead
            elif card.suit == leader[1].suit and card.rank > leader[1].rank:
                leader = (player, card)

        reason = "high trump" if leader[1].effective_suit == self.trump_suit else "high lead"

        return leader[0], reason
            

    def play_trick(self) -> tuple[Player, list[tuple[Player, Card]]]:
        print(f"\n\n--- {SUIT_ICONS[self.trump_suit]} new trick {SUIT_ICONS[self.trump_suit]} ---\n")
        for order, player in enumerate(self.players):
            print(f"player {player.id}'s turn\n{" ".join(str(card) for card in player.hand)}")

            played_card: Card = player.turn(self.trump_suit, self.lead_suit, self.pile)

            if order == 0:
                # first player sets the suit
                self.lead_suit = played_card.effective_suit

            if not played_card in player.hand:
                raise ValueError("player discarded card not in hand")

            elif played_card.effective_suit != self.lead_suit and any([card.effective_suit == self.lead_suit for card in player.hand]):
                raise ValueError("player played off-suit card when leading suit is available")

            print(f"player {player.id} played {played_card}")

            self.pile.append((player, played_card))
            player.hand.remove(played_card)

            # self.judge_leader(self.pile)
            input()

        # figure out who won the trick
        winner, reason = self.judge_leader()
        print(f"player {winner.id} won the trick ({reason})")
        return winner, self.pile


if __name__ == "__main__":
    game = Game()
    game.play_game()
