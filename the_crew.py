import models 
import random
from cards import *

class Mission:
    def __init__(self, color, number):
        self.color = color
        self.number = number
        self.modifier = []

    def __repr__(self):
        return 'Mission {} {} mod {}'.format(self.number, self.color, self.modifier)

class Communication:
    def __init__(self,card,token):
        self.card = card
        self.token = token
    
    def __repr__(self):
        return '{},{}'.format(str(self.card), self.token)

class TheCrew(models.Game):
    def __init__(self,players):

        # describe the game state
        self.drawn_missions = []
        self.hand_cards = {p:[] for p in players}
        self.hand_missions = {p:[] for p in players}
        self.communication = {p:[] for p in players}
        self.has_communicated = {p:False for p in players}
        self.resolved_missions = []
        self.discard = []
        self.fold = Fold()

        super().__init__(players)

    def end_round(self):
        # check if mission was fullfilled
        self.mission_complete()
        # promote winner to captain
        self.promote_to_captain(self.fold.leader())
        # discard fold
        self.discard.append(self.fold)
        # new empty fold
        self.fold = Fold()

    def mission_complete(self):
        # check if a mission was done in the fold
        for player,card in self.fold.content:
            if player == self.fold.leader():
                for mission in self.hand_missions[player]:
                    if mission.color == card.color and mission.number == card.number:
                        # pop mission if complete
                        print(str(player) + ' completed mission ' + str(mission))
                        self.hand_missions[player].remove(mission)
                        self.resolved_missions.append(mission)
                        break

    def admissible_cards(self,player):
        if self.fold.isempty():
            # first to play, you can play anything
            return [cards for cards in self.hand_cards[player]]
        else:
            # if you have the required color, you must play that
            required_color = [cards for cards in self.hand_cards[player] if cards.color == self.fold.color()]
            if required_color:
                return required_color
            else:
                # if not you need to cut
                trumps = [cards for cards in self.hand_cards[player] if cards.color == 'black']
                if trumps:
                    return trumps
                else:
                    # you have nothing, play whatever
                    return [cards for cards in self.hand_cards[player]]

    def play_card(self,player,card):
        if card in self.admissible_cards(player):
            self.hand_cards[player].remove(card)
            self.fold.add_card(player,card)
            print(str(player) + ' played ' + str(card))
        else:
            print('You cannot play this card!')

    def promote_to_captain(self,player):
        print(str(player) + ' is the captain!')
        player_idx = self.players.index(player)
        self.players = self.players[player_idx:] + self.players[:player_idx]

    def setup_game(self):
        CARD_COLORS = ['green', 'yellow', 'blue', 'pink']

        # create and shuffle deck of cards
        deck = [Card(color, number) for color in CARD_COLORS for number in range(1, 10)] \
            + [Card('black', number) for number in range(1, 5)]
        random.shuffle(deck)

        # deal cards to players
        while len(deck) > 0:
            # works only if the number of cards is a multiple of the number of players
            for player in self.players: 
                card = deck.pop()
                if card.color == 'black' and card.number == 4:
                    captain = player
                self.hand_cards[player].append(card)
   
        # The captain starts the first round : reorder players
        self.promote_to_captain(captain)

        # Draw a mission
        mission_deck = [Mission(color, number) for color in CARD_COLORS for number in range(1, 10)]
        random.shuffle(mission_deck)

        #TODO implement mission array
        self.drawn_missions = [mission_deck.pop(0), mission_deck.pop(0)]

        print(self)

    def game_over(self): 
        empty_hands = True
        missions_done = True
        for p in self.players:
            if self.hand_cards[p]:
                empty_hands = False
            if self.hand_missions[p]:
                missions_done = False

        #TODO check the modifiers in resolved_missions are in the right order
        if missions_done:
            print("you won!")
        
        return empty_hands or missions_done

    def __repr__(self):
        reprstr = ''
        for p in self.players:
            reprstr = reprstr + str(p) \
                + '\n\tHand: ' + ','.join([str(card) for card in self.hand_cards[p]]) \
                + '\n\tMissions: ' + ','.join([str(card) for card in self.hand_missions[p]]) \
                + '\n'  
        return reprstr

class Round(models.Round):

    def end_round(self):
        super().end_round()
        self.game.end_round()

class Human(models.Human):

    def play_setup_actions(self,game,drawn_missions):
        if self.setup_actions:
            _,action = self.menu_select(self.setup_actions)
            action(game,drawn_missions)

    def register_setup_actions(self):
        # define a list of functions that take the game as input
        self.setup_actions = [self.select_mission]

    def register_round_regular_actions(self):
        self.round_regular_actions = [self.play_card]

    def select_mission(self, game):
        if game.drawn_missions:
            index,mission = self.menu_select(game.drawn_missions)
            game.missions[self].append(mission)
            game.drawn_missions.pop(index)

    def play_card(self,game):
        # select admissible cards
        admissible_cards = game.admissible_cards(self)
        _,card_to_play = self.menu_select(admissible_cards)
        game.play_card(self,card_to_play)

class Bot(models.RandomBot):

    def register_setup_actions(self):
        # define a list of functions that take the game as input
        self.setup_actions = [self.select_mission]

    def register_round_regular_actions(self):
        self.round_regular_actions = [self.play_card]
    
    def select_mission(self,game):
        if game.drawn_missions:
            # select the first card
            game.hand_missions[self].append(game.drawn_missions[0])
            game.drawn_missions.pop(0)

    def play_card(self,game):
        # select admissible cards
        admissible_cards = game.admissible_cards(self)
        card_to_play = random.choice(admissible_cards)
        game.play_card(self,card_to_play)
