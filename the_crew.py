import models 
import random
import network
import json
from cards import *

# TODO: on top of task card modifiers, there are mission
# modifiers (no communicatiopn, ...)
# There are also modifiers that affect only one player


class TaskCard:
    def __init__(self, color, number):
        self.color = color
        self.number = number
        self.modifier = None

    def __repr__(self):
        return 'TaskCard {} {} mod {}'.format(self.number, self.color, self.modifier)

class Communication:
    def __init__(self,card,token):
        self.card = card
        self.token = token
    
    def __repr__(self):
        return '{},{}'.format(str(self.card), self.token)

class TheCrew(models.Game):
    def __init__(self, players, mission_number = 0):

        self.players = players

        self.state.num_players = len(players)
        self.state.hand_cards = {p:[] for p in range(self.state.num_players)}
        self.state.hand_tasks = {p:[] for p in range(self.state.num_players)}
        self.state.discard = []
        self.state.fold = Fold()

        # tasks
        self.state.mission_number = mission_number
        with open('the_crew_missions.json','r') as fp:
            self.state.mission_list = json.load(fp)
        self.state.num_tasks = self.state.mission_list[mission_number][0]
        self.state.modifiers = self.state.mission_list[mission_number][1]
        self.state.mission_description = self.state.mission_list[mission_number][2]
        self.state.drawn_tasks = []
        self.state.resolved_tasks = []
        self.state.win = False
        self.state.current_player_idx = 0

        if self.state.mission_number == 4:
            # additional state variables
            self.state.player_state = {}
            self.state.is_sick = None
        
        print(self.state.mission_description)

    def task_complete(self):
        # check if a task or more was done in the fold
        for player_idx,card in self.state.fold.content:
            if player_idx == self.state.fold.leader():
                for task in self.state.hand_tasks[player_idx]:
                    if task.color == card.color and task.number == card.number:
                        print(str(self.players[player_idx]) + ' completed task ' + str(task))
                        self.state.hand_tasks[player_idx].remove(task)
                        self.state.resolved_tasks.append(task)
                        # TODO: the rule states that if two tasks are done in 
                        # the same fold and they have modifiers (like 1 and 2)
                        # they are considered solved in the right order no 
                        # matter the order of those cards in the fold
                        
    def promote_to_captain(self,player_idx):
        print(str(self.players[player_idx]) + ' is the captain!')
        self.players = self.players[player_idx:] + self.players[:player_idx]

    def setup_game(self):
        CARD_COLORS = ['green', 'yellow', 'blue', 'pink']
        TRUMP_COLOR = 'black'

        # create and shuffle deck of cards
        deck = [Card(color, number, TRUMP_COLOR) for color in CARD_COLORS for number in range(1, 10)] \
            + [Card(TRUMP_COLOR, number, TRUMP_COLOR) for number in range(1, 5)]
        random.shuffle(deck)

        # deal cards to players
        while deck:
            for player_idx in range(self.state.num_players): 
                if deck:
                    card = deck.pop()
                    if card.color == 'black' and card.number == 4:
                        captain = player_idx
                    self.state.hand_cards[player_idx].append(card)
   
        # The captain starts the first round : reorder players
        self.promote_to_captain(captain)

        # Draw tasks
        task_deck = [TaskCard(color, number) for color in CARD_COLORS for number in range(1, 10)]
        random.shuffle(task_deck)

        for idx in range(self.state.num_tasks):
            task = task_deck.pop(0)
            if idx < len(self.state.modifiers):
                task.modifier = self.state.modifiers[idx]
            self.self.state.drawn_tasks.append(task)

        print(self)

    def failed_mission(self):

        if self.state.mission_number == 4:
            if self.state.discard:
                if self.state.discard[-1].leader() == self.state.is_sick:
                    return True

        # normal mission rules 
        for (idx,task) in enumerate(self.state.resolved_tasks):
            if task.modifier == "1" and idx != 0:
                return True
            elif task.modifier == "2" and idx != 1:
                return True
            elif task.modifier == "3" and idx != 2:
                return True
            elif task.modifier == "4" and idx != 3:
                return True
            elif task.modifier == "5" and idx != 4:
                return True
            elif task.modifier == "Ω" and idx != self.state.num_tasks-1:
                return True

            elif task.modifier == ">":
                if (">>" or  ">>>" or ">>>>") in self.state.resolved_tasks[:idx]:
                    return True
            elif task.modifier == ">>":
                if not ">" in self.state.resolved_tasks[:idx]:
                    return True
                elif (">>>" or ">>>>") in self.state.resolved_tasks[:idx]:
                    return True
            elif task.modifier == ">>>":
                if not (">" and ">>") in self.state.resolved_tasks[:idx]:
                    return True
                elif ">>>>" in self.state.resolved_tasks[:idx]:
                    return True
            elif task.modifier == ">>>>":
                if not (">" and ">>" and ">>>") in self.state.resolved_tasks[:idx]:
                    return True
        return False

    def game_over(self): 

        if self.failed_mission():
            return True

        empty_hands = False
        tasks_done = True
        for player_idx in range(self.state.num_players):
            if not self.state.hand_cards[player_idx]:
                empty_hands = True
            if self.state.hand_tasks[player_idx]:
                tasks_done = False

        if not self.state.mission_number == 4: 
            if tasks_done:
                self.state.win = True
                return True
        
        return empty_hands

    def play(self):
        print('Let\'s play!')
        
        # play setup actions
        if self.state.mission_number == 4:    
            # the crewmates play first
            for player_idx,player in enumerate(self.players[1:]):
                self.state.current_player_idx = player_idx+1
                player.play_setup_actions(self.state)
            # then the captain
            self.state.current_player_idx = 0
            self.players[0].play_setup_actions(self.state)
        else:
            for player_idx,player in enumerate(self.players):
                self.state.current_player_idx = player_idx
                player.play_setup_actions(self.state)

        # play the game
        while not self.game_over():
            print(self)
            round = Round(self)
            round.play()

        # end game
        self.end_game()

    def end_game(self):
        if self.state.win:
            print("Congratulations, mission complete!")
        else:
            print("You lost!")

    def __repr__(self):
        reprstr = ''
        for player_idx,player in enumerate(self.players):
            reprstr = reprstr + str(player) \
                + '\n\tHand: ' + ','.join([str(card) for card in self.state.hand_cards[player_idx]]) \
                + '\n\tTasks: ' + ','.join([str(card) for card in self.state.hand_tasks[player_idx]]) \
                + '\n'  
        reprstr = reprstr + ','.join([str(task) for task in self.self.state.drawn_tasks])
        return reprstr

class Round(models.Round):

    def start_round(self):
        for player_idx,player in enumerate(self.game.players):
            self.game.state.current_player_idx = player_idx
            player.play_round_start_actions(self.game.state)

    def end_round(self):
        for player_idx,player in enumerate(self.game.players):
            self.game.state.current_player_idx = player_idx
            player.play_round_end_actions(self.game.state)

        # check if a task was fullfilled
        self.game.task_complete()
        # promote winner to captain
        self.game.promote_to_captain(self.state.fold.leader())
        # discard fold
        self.game.state.discard.append(self.state.fold)
        # new empty fold
        self.game.state.fold = Fold()

    def play(self):
        self.start_round()

        # each player plays
        for player_idx,player in enumerate(self.game.players):
            self.game.state.current_player_idx = player_idx
            player.play_round_regular_actions(self.game)
            for player_idx,player in enumerate(self.game.players):
                self.game.state.current_player_idx = player_idx
                player.play_round_interrupt_actions(self.game)
                
        self.end_round()

def admissible_cards(game_state):
    player_idx = game_state.current_player_idx

    if game_state.fold.isempty():
        # first to play, you can play anything
        return [cards for cards in game_state.hand_cards[player_idx]]
    else:
        # if you have the required color, you must play that
        required_color = [cards for cards in game_state.hand_cards[player_idx] if cards.color == game_state.fold.color()]
        if required_color:
            return required_color
        else:
            # if not you need to cut
            trumps = [cards for cards in game_state.hand_cards[player_idx] if cards.color == 'black']
            if trumps:
                return trumps
            else:
                # you have nothing, play whatever
                return [cards for cards in game_state.hand_cards[player_idx]]

class Human(models.Human):
    def register_setup_actions(self):
        # define a list of functions that take the game as input
        self.setup_actions = [self.do_setup]

    def register_round_regular_actions(self):
        self.round_regular_actions = [self.play_card]

    def do_setup(self, game_state):
        player_idx = game_state.current_player_idx
        if game_state.drawn_tasks:
            index,mission = self.menu_select(game_state.drawn_tasks)
            game_state.hand_tasks[player_idx].append(mission)
            game_state.drawn_tasks.pop(index)
        if gamestate.mission_number == 4:
            self.special_mission_4(game_state)
        
    def special_mission_4(self, game_state):
        player_idx = game_state.current_player_idx
        if player_idx == 0: # captain
            _,game_state.is_sick = self.menu_select(list(range(1,game_state.num_players)))
            print("{} is sick".format(game_state.is_sick))
        else: # crewmates
            _,game_state.player_state[player_idx] = self.menu_select(["good","bad"])
            print("{} is feeling ".format(self) + game_state.player_state[player_idx])

    def play_card(self,game_state):
        # select admissible cards
        player_idx = game_state.current_player_idx
        cards_list = admissible_cards(game_state)
        _,card_to_play = self.menu_select(cards_list)
        game_state.hand_cards[player_idx].remove(card_to_play)
        game_state.fold.add_card(player_idx,card_to_play)

class Bot(models.RandomBot):

    def register_setup_actions(self):
        # define a list of functions that take the game as input
        self.setup_actions = [self.do_setup]

    def register_round_regular_actions(self):
        self.round_regular_actions = [self.play_card]
    
    def special_mission_4(self, game_state):
        player_idx = game_state.current_player_idx
        if player_idx == 0: # captain
            game_state.is_sick = random.choice(list(range(1,game_state.num_players)))
            print("{} is sick".format(game_state.is_sick))
        else: # crewmates
            game_state.player_state[player_idx] = random.choice(["good","bad"])
            print("{} is feeling ".format(player_idx) + game_state.player_state[player_idx])

    def do_setup(self,game_state):
        player_idx = game_state.current_player_idx
        if game_state.drawn_tasks:
            # select the first card
            game_state.hand_tasks[player_idx].append(game_state.drawn_tasks[0])
            game_state.drawn_tasks.pop(0)
        if game_state.mission_number == 4:
            self.special_mission_4(game_state)

    def play_card(self,game_state):
        # select admissible cards
        player_idx = game_state.current_player_idx
        cards_list = admissible_cards(game_state)
        card_to_play = random.choice(cards_list)
        game_state.hand_cards[player_idx].remove(card_to_play)
        game_state.fold.add_card(player_idx,card_to_play)

class SmartBot(models.Player):
    #TODO
    pass
