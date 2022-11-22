import random

class Deck:
    def __init__(self):
        self.cards = []

    def isempty(self):
        if self.cards:
            return False
        else:
            return True

    def shuffle(self):
        random.shuffle(self.cards)

    def cut(self):
        idx = random.randrange(len(self.card))
        self.cards = self.cards[idx:] + self.cards[:idx]

    def draw(self):
        return self.cards.pop(0)

class Card:
    def __init__(self, color, number, trump_color=None):
        self.color = color
        self.number = number
        self.trump_color = trump_color

    def __repr__(self):
        return '{} {}'.format(self.color, self.number)

    def __eq__(self, other):
        return self.color == other.color and self.number == other.number

    def __gt__(self, other):
        if self.color == other.color:
            return self.number > other.number
        if self.trump_color:
            if self.color == self.trump_color and other.color != self.trump_color:
                return True
            if self.color != self.trump_color and other.color == self.trump_color:
                return False

class Fold:
    def __init__(self):
        # list of (player,card) tuples
        self.content = []

    def __repr__(self):
        return ','.join([str(p) + ': ' + str(card) + '\n' for p,card in self.content])

    def isempty(self):
        if self.content:
           return False
        else:
            return True

    def add_card(self,player,card):
        self.content.append((player,card))

    def color(self):
        if self.content:
            first_player, first_card = self.content[0]
            return first_card.color
        else:
            return None

    def leader(self):
        if self.content:
            return max(self.content,key=lambda item: item[1])[0]
        else:
            return None

            