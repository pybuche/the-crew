import random

# Tentative definition of general game components 

# A Session can have several Game (the crew, coinche)
# A Game has several Rounds
# A Round as several Turns (usually = #players)
# A Turn can feature several actions

class Game:
    def __init__(self,state = None):
        self.players = [] # list of players in the game
        self.rounds = [] # list of played rounds
        self.state = state # determines the game state (map, tokens, deck, discard pile...)
        self.winner = []

    def setup_game(self):
        # initialize the game state (shuffle and deal cards, distribute tokens,...)
        # determine which player starts the first round 
        # This stage may or may not require actions from the players
        # the crew: determine which mission to play
        # tarot or coinche : annonces
        pass

    def game_over(self): 
        # use the game state to determine if the game is over
        # determine the winner if any
        # return true or false
        return False

    def play(self):
        # play the game
        self.setup_game()
        while ~self.game_over:
            round = Round(self)
            round.play()

class Round:
    def __init__(self,game):
        self.game = game # access game state and players
        self.turns = [] # list of turns played 
        self.events = [] # events that may occur besides players playing their turns

    def start_round(self):
        # process any events that may occur before player start to play
        # (i.e. Galerapagos weather card, food and water supply)
        pass
    
    def end_round(self):
        # process any events that may occur after players have played
        # (i.e. determine who is the next first player for the next round)
        pass

    def play(self):
        self.start_round()
        # each player plays
        
        self.end_round()

class Turn:
    def __init__(self):
        self.player = None # the player of the turn
        self.actions = [] # list of actions performed during the turn


    
class Player: # Players have a name, a score 
    def __init__(self):
        self.name = None
        self.score = None
        self.setup_actions = [] # during setup of the game
        self.start_actions = [] # at the beginning of each round
        self.regular_actions = [] # actions during the turn
        self.interrupt_actions = [] # actions during the another player's turn 
        self.end_actions = [] # actions at the end of the round

    def register_setup_action(self):
        self.setup_actions = []

    def register_start_actions(self):
        self.start_actions = []

    def register_regular_actions(self):
        self.regular_actions = []

    def register_interrupt_actions(self):
        

class Bot(Player): # Bots are players that can implement automatic strategies
    pass

class Human(Player): # Humans are asked what to play
    pass
