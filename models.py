import random

class Game:
    def __init__(self,players):
        self.players = players
        self.setup_game()

    def setup_game(self):
        # initialize the game state (shuffle and deal cards, distribute tokens,...)
        # determine which player starts the first round 

        # This stage may or may not require actions from the players
        # the crew: determine which mission to play
        # tarot or coinche : annonces
        pass
        
    def end_game(self):
        # perform end of game actions, determine who won
        pass

    def game_over(self): 
        # use the game state to determine if the game is over
        # determine the winner if any
        # return true or false
        return False

    def play(self):
        # play setup actions
        for p in self.players:
            p.play_setup_actions(self)

        # play the game
        while not self.game_over():
            print(self)
            round = Round(self)
            round.play()

        # end game
        self.end_game()

class Round:
    def __init__(self,game):
        self.game = game # access game state and players

    def start_round(self):
        # process any events that may occur before player start to play
        # (i.e. Galerapagos weather card, food and water supply)

        # allow players to play beginning of turn actions
        for p in self.game.players:
            p.play_round_start_actions(self.game)
    
    def end_round(self):
        # process any events that may occur after players have played
        # (i.e. determine who is the next first player for the next round)

        # allow players to do end of turn actions
        for p in self.game.players:
            p.play_round_end_actions(self.game)
            
    def play(self):
        self.start_round()

        # each player plays
        for p in self.game.players:
            p.play_round_regular_actions(self.game)
            for p in self.game.players:
                p.play_round_interrupt_actions(self.game)
                
        self.end_round()
 
class Player: # Players have a name, a score 
    def __init__(self,name):
        self.name = name
        self.register_setup_actions() # during setup phase
        self.register_round_start_actions() # at the beginning of each round
        self.register_round_regular_actions() # actions during the turn
        self.register_round_interrupt_actions() # actions during the another player's turn 
        self.register_round_end_actions() # actions at the end of the round
        self.register_end_actions() # actions at the end of the round

    def register_setup_actions(self):
        # define a list of functions that take the game as input
        self.setup_actions = []

    def register_end_actions(self):
        self.end_actions = []

    # round specific actions
    def register_round_start_actions(self):
        self.round_start_actions = []

    def register_round_regular_actions(self):
        self.round_regular_actions = []

    def register_round_interrupt_actions(self):
        self.round_interrupt_actions = []

    def register_round_end_actions(self):
        self.round_end_actions = []

class RandomBot(Player):
    def do_action(self,game,action_list):
        if action_list:
            action = random.choice(action_list)
            action(game)

    def play_setup_actions(self,game):
        self.do_action(game,self.setup_actions)
    
    def play_end_actions(self,game):
        self.do_action(game,self.end_actions)

    def play_round_start_actions(self,game):
        self.do_action(game,self.round_start_actions)

    def play_round_regular_actions(self,game):
        self.do_action(game,self.round_regular_actions)

    def play_round_interrupt_actions(self,game):
        self.do_action(game,self.round_interrupt_actions)

    def play_round_end_actions(self,game):
        self.do_action(game,self.round_end_actions)

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

    def do_action(self,game,action_list):
        if action_list:
            _,action = self.menu_select(action_list)
            action(game)

    def play_setup_actions(self,game):
       self.do_action(game,self.setup_actions)
    
    def play_end_actions(self,game):
        self.do_action(game,self.end_actions)

    def play_round_start_actions(self,game):
        self.do_action(game,self.round_start_actions)

    def play_round_regular_actions(self,game):
        self.do_action(game,self.round_regular_actions)

    def play_round_interrupt_actions(self,game):
        self.do_action(game,self.round_interrupt_actions)

    def play_round_end_actions(self,game):
        self.do_action(game,self.round_end_actions)

    def __repr__(self):
        return "Human_{}".format(self.name)