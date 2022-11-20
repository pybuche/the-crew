import models 
import random

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

class Communication:
    def __init__(self,card,token):
        self.card = card
        self.token = token
    
    def __repr__(self):
        return '{},{}'.format(str(self.card), self.token)

class GameState:
    def __init__(self,players):
        self.players = players
        self.hands = {p:[] for p in players}
        self.missions = {p:[] for p in players}
        self.communication = {p:[] for p in players}
        self.has_communicated = {p:False for p in players}
        self.discard = []

    def promote_to_captain(self,player_idx):
         self.players = [self.players[(idx + player_idx) % len(self.players)] for idx in range(len(self.players))]

    def __repr__(self):
        reprstr = ''
        for p in self.players:
            reprstr = reprstr + str(p) \
                + '\n\tHand: ' + ','.join([str(card) for card in self.hands[p]]) \
                + '\n\tMissions: ' + ','.join([str(card) for card in self.missions[p]]) \
                + '\n'
        reprstr = reprstr + 'Discard: ' + ','.join([str(card) for card in self.discard])
        return reprstr

class TheCrew(models.Game):

    def game_over(self):
        empty_hands = True
        missions_done = True
        for p in self.state.players:
            if self.state.hands[p]:
                empty_hands = False
            if self.state.missions[p]:
                missions_done = False

        if missions_done:
            print("you won!")
        
        return empty_hands or missions_done

    def setup_game(self):
        CARD_COLORS = ['green', 'yellow', 'blue', 'pink']

        # create and shuffle deck of cards
        deck = [Card(color, number) for color in CARD_COLORS for number in range(1, 10)] \
            + [Card('black', number) for number in range(1, 5)]
        random.shuffle(deck)

        # deal cards to players
        while len(deck) > 0:
            # works only if the number of cards is a multiple of the number of players
            for (index, player) in enumerate(self.state.players): 
                card = deck.pop()
                if card.color == 'black' and card.number == 4:
                    captain_index = index
                self.state.hands[player].append(card)
   
        # The captain starts the first round : reorder players
        self.state.promote_to_captain(captain_index)

        # Draw a mission
        mission_deck = [Mission(color, number) for color in CARD_COLORS for number in range(1, 10)]
        random.shuffle(mission_deck)

        #TODO implement mission array
        drawn_missions = [mission_deck.pop(0), mission_deck.pop(0)]

        for p in self.state.players:
            p.play_setup_actions(self.state, drawn_missions)

class Round(models.Round):
    pass

class Human(models.Human):

    def play_setup_actions(self,game_state,drawn_missions):
        if self.setup_actions:
            _,action = self.menu_select(self.setup_actions)
            action(game_state,drawn_missions)

    def register_setup_actions(self):
        # define a list of functions that take the game as input
        self.setup_actions = [self.select_mission]

    def select_mission(self, game_state,drawn_missions):
        if drawn_missions:
            index,mission = self.menu_select(drawn_missions)
            game_state.missions[self].append(mission)
            drawn_missions.pop(index)
        
class Bot(models.Bot):
    
    def play_setup_actions(self,game_state,drawn_missions):
        if self.setup_actions:
            action = random.choice(self.setup_actions)
            action(game_state,drawn_missions)

    def register_setup_actions(self):
        # define a list of functions that take the game as input
        self.setup_actions = [self.select_mission]

    def select_mission(self,game_state,drawn_missions):
        if drawn_missions:
            # select the first card
            game_state.missions[self].append(drawn_missions[0])
            drawn_missions.pop(0)
