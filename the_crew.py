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

class GameState:
    def __init__(self,players):
        self.players = players
        self.hands = {p:[] for p in players}
        self.missions = {p:[] for p in players}
        self.communication = {p:[] for p in players}
        self.has_communicated = {p:False for p in players}
        self.discard = []
        self.fold = Fold()

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
            for mission in self.missions[player]:
                if mission.color == card.color and mission.number == card.number:
                    # pop mission if complete
                    print(str(player) + 'completed mission' + str(mission))
                    self.missions[player].remove(mission)
                    break

    def admissible_cards(self,player):
        if self.fold.isempty():
            # first to play, you can play anything
            return [cards for cards in self.hands[player]]
        else:
            # if you have the required color, you must play that
            required_color = [cards for cards in self.hands[player] if cards.color == self.fold.color()]
            if required_color:
                return required_color
            else:
                # if not you need to cut
                trumps = [cards for cards in self.hands[player] if cards.color == 'black']
                if trumps:
                    return trumps
                else:
                    # you have nothing, play whatever
                    return [cards for cards in self.hands[player]]

    def play_card(self,player,card):
        if card in self.admissible_cards(player):
            self.hands[player].remove(card)
            self.fold.add_card(player,card)
        else:
            print('You cannot play this card!')

    def promote_to_captain(self,player):
        player_idx = self.players.index(player)
        self.players = self.players[player_idx:] + self.players[:player_idx]

    def __repr__(self):
        reprstr = ''
        for p in self.players:
            reprstr = reprstr + str(p) \
                + '\n\tHand: ' + ','.join([str(card) for card in self.hands[p]]) \
                + '\n\tMissions: ' + ','.join([str(card) for card in self.missions[p]]) \
                + '\n'
        reprstr = reprstr + '\nFold: ' + str(self.fold)      
        reprstr = reprstr + '\nDiscard: ' + ','.join([str(card) for card in self.discard])
        
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
            for player in self.state.players: 
                card = deck.pop()
                if card.color == 'black' and card.number == 4:
                    captain = player
                self.state.hands[player].append(card)
   
        # The captain starts the first round : reorder players
        self.state.promote_to_captain(captain)

        # Draw a mission
        mission_deck = [Mission(color, number) for color in CARD_COLORS for number in range(1, 10)]
        random.shuffle(mission_deck)

        #TODO implement mission array
        drawn_missions = [mission_deck.pop(0), mission_deck.pop(0)]

        for p in self.state.players:
            p.play_setup_actions(self.state, drawn_missions)

class Round(models.Round):

    def end_round(self):
        super().end_round()
        self.game.state.end_round()

class Human(models.Human):

    def play_setup_actions(self,game_state,drawn_missions):
        if self.setup_actions:
            _,action = self.menu_select(self.setup_actions)
            action(game_state,drawn_missions)

    def register_setup_actions(self):
        # define a list of functions that take the game as input
        self.setup_actions = [self.select_mission]

    def register_regular_actions(self):
        self.regular_actions = [self.play_card]

    def select_mission(self, game_state,drawn_missions):
        if drawn_missions:
            index,mission = self.menu_select(drawn_missions)
            game_state.missions[self].append(mission)
            drawn_missions.pop(index)

    def play_card(self,game_state):
        # select admissible cards
        admissible_cards = game_state.admissible_cards(self)
        _,card_to_play = self.menu_select(admissible_cards)
        game_state.play_card(self,card_to_play)


class Bot(models.Bot):
    
    def play_setup_actions(self,game_state,drawn_missions):
        if self.setup_actions:
            action = random.choice(self.setup_actions)
            action(game_state,drawn_missions)

    def register_setup_actions(self):
        # define a list of functions that take the game as input
        self.setup_actions = [self.select_mission]

    def register_regular_actions(self):
        self.regular_actions = [self.play_card]
    
    def select_mission(self,game_state,drawn_missions):
        if drawn_missions:
            # select the first card
            game_state.missions[self].append(drawn_missions[0])
            drawn_missions.pop(0)

    def play_card(self,game_state):
        # select admissible cards
        admissible_cards = game_state.admissible_cards(self)
        card_to_play = random.choice(admissible_cards)
        game_state.play_card(self,card_to_play)
