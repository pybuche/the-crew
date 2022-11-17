import random

def draw_cards(card_deck, players):
    random.shuffle(card_deck)
    while len(card_deck) > 0:
        for (index,player) in enumerate(players):
            card = card_deck.pop()
            print('giving {} to {}'.format(card, player))
            if card.color == 'black' and card.number == 4:
                captain_name = player.name
                captain_index = index
            player.add_card(card)
    print('{} is the captain!'.format(captain_name))
    return captain_index

def draw_mission(mission_deck, players, mission_number):
    mission = MISSION_DATABASE[mission_number]
    if mission[0] == 0:
        # special mission
        modifiers = mission[1]
        if modifier[0] == -1: # first special mission
            pass
        elif modifier[0] == -2: # second special mission
            pass
    else:
        # regular mission
        number_of_cards = mission[0]
        modifiers = mission[1]
        mission_list = mission_deck[0:number_of_cards]
        # put the mission back at the end of the deck 
        mission_deck = [mission_deck[(idx + number_of_cards) % len(mission_deck)] for idx in range(len(mission_deck))]
        # deal missions to players starting with captain
        

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
    def __init__(self,color,number):
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

    def add_card(self, card):
        self.cards.append(card)

    def play(self, fold):
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
                    random.shuffle(self.cards)
                    card = self.cards.pop()
                else:
                    max_black_card = max(black_cards, key=lambda card: card.number)
                    self.cards.remove(max_black_card)
                    card = max_black_card
            else:
                max_card_from_color = max(cards_with_same_color, key=lambda card: card.number)
                self.cards.remove(max_card_from_color)
                card = max_card_from_color


        fold.add_card(card)
        print('{} plays {} on fold {}'.format(self.name, card, fold))


class Turn:
    def __init__(self, players):
        self.fold = Fold()
        self.players = players

    def play(self):
        if len(self.players[0].cards) == 0:
            print('Game is finished!!!')
            return

        for player in self.players:
            player.play(self.fold)

        winner_index = self.fold.get_winner_index()
        print('Winner is {}'.format(self.players[winner_index].name))

        new_players_order = [self.players[(idx + winner_index) % len(self.players)] for idx in range(len(self.players))]
        new_turn = Turn(new_players_order)
        return new_turn.play()
