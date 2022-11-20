from models import *

class TheCrew(Game):
    pass

class Card:
    def __init__(self, color, number):
        self.color = color
        self.number = number

    def __repr__(self):
        return '{} {}'.format(self.color, self.number)

    def __eq__(self, other):
        return self.color == other.color and self.number == other.number

    def __gt__(self, other):
        if self.color == other.color:
            return self.number > other.number
        if self.color == 'black' and other.color != 'black':
            return True
        if self.color != 'black' and other.color == 'black':
            return False

class Mission:
    def __init__(self, color, number):
        self.color = color
        self.number = number
        self.modifier = []

    def __repr__(self):
        return 'Mission {} {} mod {}'.format(self.number, self.color, self.modifier)

class Fold:
    def __init__(self):
        self.cards = []

    def __repr__(self):
        return '({})'.format(','.join([str(c) for c in self.cards]))

    def add_card(self, card):
        self.cards.append(card)

    def get_winner_index(self):
        fold_color = self.cards[0].color

        best_index = 0
        best_card = self.cards[0]

        for card_index in range(1, len(self.cards)):
            current_card = self.cards[card_index]
            if current_card.color != 'black' and current_card.color != fold_color:
                continue
            if current_card > best_card:
                best_card = current_card
                best_index = card_index

        return best_index


class Player:
    def __init__(self, name):
        self.name = name
        self.cards = []
    def __repr__(self):
        return '{} ({})'.format(self.name, ','.join([str(card) for card in self.cards]))

    @property
    def colors(self):
        return {
            "green": list(filter(lambda card: card.color == "green", self.cards)),
            "yellow": list(filter(lambda card: card.color == "yellow", self.cards)),
            "blue": list(filter(lambda card: card.color == "blue", self.cards)),
            "pink": list(filter(lambda card: card.color == "pink", self.cards)),
            "black": list(filter(lambda card: card.color == "black", self.cards)),
        }

    def add_card(self, card):
        self.cards.append(card)

    def find_card_to_play(self, playable_cards, fold, mission, player_index, captain_index):
        winner_index = fold.get_winner_index()

        if len(playable_cards) == 1:
            return playable_cards[0]

        if mission in playable_cards:
            # If the captain is winning the fold and you have the card, you play it!
            if winner_index == captain_index:
                return mission
            # Or if the captain plays after you and the fold is weak, you play it as well (betting)
            if (captain_index > player_index and max(card.number for card in fold.cards) < 5):
                return mission

        min_or_max = max if player_index == captain_index else min
        everything_but_mission = list(filter(lambda card: card != mission, playable_cards))
        return min_or_max(everything_but_mission)

    def play(self, fold, mission, player_index, captain_index):
        card = None

        if len(fold.cards) == 0:
            # if fold is empty, play random
            random.shuffle(self.cards)
            card = self.cards.pop()
        else:
            card_color = fold.cards[0].color
            cards_with_same_color = list(filter(lambda card: card.color == card_color, self.cards))

            if len(cards_with_same_color) == 0:
                black_cards = list(filter(lambda card: card.color == 'black', self.cards))
                if len(black_cards) == 0:
                    card = self.find_card_to_play(self.cards, fold, mission, player_index, captain_index)
                    self.cards.remove(card)
                else:
                    max_black_card = max(black_cards, key=lambda card: card.number)
                    self.cards.remove(max_black_card)
                    card = max_black_card
            else:
                card = self.find_card_to_play(cards_with_same_color, fold, mission, player_index, captain_index)
                self.cards.remove(card)

        fold.add_card(card)
        print('{} plays {} on fold {}'.format(self.name, card, fold))


class Turn:
    def __init__(self, players, index, mission):
        self.fold = Fold()
        self.players = players
        self.index = index
        self.mission = mission

    # Return winner_index, mission_completed
    def play(self, captain_index):
        print('##########################')
        print('Turn n°{} | Mission {}'.format(self.index, self.mission))
        print('--------------------------')
        for index, player in enumerate(self.players):
            player.play(self.fold, self.mission, index, captain_index)

        winner_index = self.fold.get_winner_index()
        mission_completed = self.mission in self.fold.cards
        return winner_index, mission_completed