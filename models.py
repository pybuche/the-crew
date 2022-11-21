import random

# General structure of a Game

class GameState:
    def __init__(self,players):
        self.players = players 
        ## add the relevant data structures to describe the state of the game

class Game:
    def __init__(self,state):
        self.rounds = [] # list of played rounds
        self.state = state # determines the game state (map, tokens, deck, discard pile...)
        self.history = []
        self.setup_game()

    def setup_game(self):
        # initialize the game state (shuffle and deal cards, distribute tokens,...)
        # determine which player starts the first round 

        # This stage may or may not require actions from the players
        # the crew: determine which mission to play
        # tarot or coinche : annonces
        for p in self.state.players:
            p.play_setup_action(self.state)

    def game_over(self): 
        # use the game state to determine if the game is over
        # determine the winner if any
        # return true or false
        return False

    def play(self):
        # play the game
        while not self.game_over:
            round = Round(self)
            round.play()
            print(self.state)

class Round:
    def __init__(self,game):
        self.game = game # access game state and players

    def start_round(self):
        # process any events that may occur before player start to play
        # (i.e. Galerapagos weather card, food and water supply)

        # allow players to play beginning of turn actions
        for p in self.game.state.players:
            p.play_start_actions(self.game.state)
    
    def end_round(self):
        # process any events that may occur after players have played
        # (i.e. determine who is the next first player for the next round)

        # allow players to do end of turn actions
        for p in self.game.state.players:
            p.play_end_actions(self.game.state)
            
    def play(self):
        self.start_round()

        # each player plays
        for p in self.game.state.players:
            p.play_regular_actions(self.game.state)
            for p in self.game.state.players:
                p.play_interrupt_actions(self.game.state)
                
        self.end_round()
 
class Player: # Players have a name, a score 
    def __init__(self,name):
        self.name = name
        self.register_setup_actions() # during setup phase
        self.register_start_actions() # at the beginning of each round
        self.register_regular_actions() # actions during the turn
        self.register_interrupt_actions() # actions during the another player's turn 
        self.register_end_actions() # actions at the end of the round

    def register_setup_actions(self):
        # define a list of functions that take the game as input
        self.setup_actions = []

    def register_start_actions(self):
        self.start_actions = []

    def register_regular_actions(self):
        self.regular_actions = []

    def register_interrupt_actions(self):
        self.interrupt_actions = []

    def register_end_actions(self):
        self.end_actions = []

class Bot(Player): # Bots are players that can implement automatic strategies
    def play_setup_actions(self,game_state):
        if self.setup_actions:
            action = random.choice(self.setup_actions)
            action(game_state)

    def play_start_actions(self,game_state):
        if self.start_actions:
            action = random.choice(self.start_actions)
            action(game_state)

    def play_regular_actions(self,game_state):
        if self.regular_actions:
            action = random.choice(self.regular_actions)
            action(game_state)

    def play_interrupt_actions(self,game_state):
        if self.interrupt_actions:
            action = random.choice(self.interrupt_actions)
            action(game_state)

    def play_end_actions(self,game_state):
        if self.end_actions:
            action = random.choice(self.end_actions)
            action(game_state)

    def __repr__(self):
        return "Bot_{}".format(self.name)

class Human(Player): # Humans are asked what to play
    def menu_select(self,options):
        if len(options) == 1:
            print(options)
            return 0,options[0]
        else:
            print(options)
            index = input(">> ")
            try:
                index = int(index)
                selection = options[index]
            except:
                print("Invalid selection, please try again.\n")
                self.menu_select(options)
            return index,selection

    def play_setup_actions(self,game_state):
        if self.setup_actions:
            _,action = self.menu_select(self.setup_actions)
            action(game_state)

    def play_start_actions(self,game_state):
        if self.start_actions:
            _,action = self.menu_select(self.start_actions)
            action(game_state)

    def play_regular_actions(self,game_state):
        if self.regular_actions:
            _,action = self.menu_select(self.regular_actions)
            action(game_state)

    def play_interrupt_actions(self,game_state):
        if self.interrupt_actions:
            _,action = self.menu_select(self.interrupt_actions)
            action(game_state)

    def play_end_actions(self,game_state):
        if self.end_actions:
            _,action = self.menu_select(self.end_actions)
            action(game_state)

    def __repr__(self):
        return "Human_{}".format(self.name)