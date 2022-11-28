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

class GameState:
    def __init__(self,players,mission_number):
        self.num_players = len(players)
        self.player_order = [player_idx for player_idx in range(self.num_players)]
        self.player_names = [p.name for p in players]
        self.hand_cards = {p:[] for p in range(self.num_players)}
        self.hand_tasks = {p:[] for p in range(self.num_players)}
        self.discard = []
        self.fold = Fold()

        # tasks
        self.mission_number = mission_number
        with open('the_crew_missions.json','r') as fp:
            self.mission_list = json.load(fp)
        self.num_tasks = self.mission_list[mission_number][0]
        self.modifiers = self.mission_list[mission_number][1]
        self.mission_description = self.mission_list[mission_number][2]
        self.drawn_tasks = []
        self.resolved_tasks = []
        self.win = False
        self.current_player_idx = 0

        if self.mission_number == 4:
            # additional state variables
            self.player_state = {}
            self.is_sick = None

        self.setup_game()

        print(self.mission_description)
        print(self)

    def setup_game(self):
        CARD_COLORS = ['green', 'yellow', 'blue', 'pink']
        TRUMP_COLOR = 'black'

        # create and shuffle deck of cards
        deck = [Card(color, number, TRUMP_COLOR) for color in CARD_COLORS for number in range(1, 10)] \
            + [Card(TRUMP_COLOR, number, TRUMP_COLOR) for number in range(1, 5)]
        random.shuffle(deck)

        # deal cards to players
        while deck:
            for player_idx in range(self.num_players): 
                if deck:
                    card = deck.pop()
                    if card.color == 'black' and card.number == 4:
                        captain = player_idx
                    self.hand_cards[player_idx].append(card)
   
        # The captain starts the first round : reorder players
        self.promote_to_captain(captain)

        # Draw tasks
        task_deck = [TaskCard(color, number) for color in CARD_COLORS for number in range(1, 10)]
        random.shuffle(task_deck)

        for task_idx in range(self.num_tasks):
            task = task_deck.pop(0)
            if task_idx < len(self.modifiers):
                task.modifier = self.modifiers[task_idx]
            self.drawn_tasks.append(task)

    def promote_to_captain(self,player_idx):
        print(str(self.player_names[player_idx]) + ' is the captain!')
        idx = self.player_order.index(player_idx)
        self.player_order = self.player_order[idx:] + self.player_order[:idx]

    def admissible_cards(self):
        player_idx = self.current_player_idx
        if self.fold.isempty():
            # first to play, you can play anything
            return [cards for cards in self.hand_cards[player_idx]]
        else:
            # if you have the required color, you must play that
            required_color = [cards for cards in self.hand_cards[player_idx] if cards.color == self.fold.color()]
            if required_color:
                return required_color
            else:
                # if not you need to cut
                trumps = [cards for cards in self.hand_cards[player_idx] if cards.color == 'black']
                if trumps:
                    return trumps
                else:
                    # you have nothing, play whatever
                    return [cards for cards in self.hand_cards[player_idx]]

    def task_complete(self):
        # check if a task or more was done in the fold
        for player_idx,card in self.fold.content:
            if player_idx == self.fold.leader():
                for task in self.hand_tasks[player_idx]:
                    if task.color == card.color and task.number == card.number:
                        print(str(player_idx) + ' completed task ' + str(task))
                        self.hand_tasks[player_idx].remove(task)
                        self.resolved_tasks.append(task)
                        # TODO: the rule states that if two tasks are done in 
                        # the same fold and they have modifiers (like 1 and 2)
                        # they are considered solved in the right order no 
                        # matter the order of those cards in the fold

    def play_card(self,player_idx,card):
        self.hand_cards[player_idx].remove(card)
        self.fold.add_card(player_idx,card)

    def failed_mission(self):
        if self.mission_number == 4:
            if self.discard:
                if self.discard[-1].leader() == self.is_sick:
                    return True

        # normal mission rules 
        for (idx,task) in enumerate(self.resolved_tasks):
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
            elif task.modifier == "Ω" and idx != self.num_tasks-1:
                return True

            elif task.modifier == ">":
                if (">>" or  ">>>" or ">>>>") in self.resolved_tasks[:idx]:
                    return True
            elif task.modifier == ">>":
                if not ">" in self.resolved_tasks[:idx]:
                    return True
                elif (">>>" or ">>>>") in self.resolved_tasks[:idx]:
                    return True
            elif task.modifier == ">>>":
                if not (">" and ">>") in self.resolved_tasks[:idx]:
                    return True
                elif ">>>>" in self.resolved_tasks[:idx]:
                    return True
            elif task.modifier == ">>>>":
                if not (">" and ">>" and ">>>") in self.resolved_tasks[:idx]:
                    return True
        return False

    def game_over(self): 
        if self.failed_mission():
            return True

        empty_hands = False
        tasks_done = True
        for player_idx in range(self.num_players):
            if not self.hand_cards[player_idx]:
                empty_hands = True
            if self.hand_tasks[player_idx]:
                tasks_done = False

        if not self.mission_number == 4: 
            if tasks_done:
                self.win = True
                return True
        
        return empty_hands

    def __repr__(self):
        reprstr = ''
        for player_idx in self.player_order:
            reprstr = reprstr + str(self.player_names[player_idx]) \
                + '\n\tHand: ' + ','.join([str(card) for card in self.hand_cards[player_idx]]) \
                + '\n\tTasks: ' + ','.join([str(card) for card in self.hand_tasks[player_idx]]) \
                + '\n'  
        reprstr = reprstr + 'Tasks:\n\t'
        reprstr = reprstr + ','.join([str(task) for task in self.drawn_tasks])
        return reprstr

class TheCrew(models.Game):
    def __init__(self, players, mission_number = 0):
        self.players = players
        self.state = GameState(players,mission_number)    

    def play(self):
        print('Let\'s play!')
        # play setup actions
        if self.state.mission_number == 4:    
            # the crewmates play first
            for player_idx in self.state.player_order[1:]:
                self.state.current_player_idx = player_idx
                player = self.players[player_idx]
                player.play_setup_actions(self.state)
            # then the captain
            captain = self.state.player_order[0]
            self.state.current_player_idx = captain
            player = self.players[captain]
            player.play_setup_actions(self.state)
        else:
            for player_idx in self.state.player_order:
                self.state.current_player_idx = player_idx
                player = self.players[player_idx]
                player.play_setup_actions(self.state)

        # play the game
        while not self.state.game_over():
            print(self.state)
            round = Round(self)
            round.play()

        # end game
        self.end_game()

    def end_game(self):
        # do end of game actions 

        # print 
        if self.state.win:
            print("Congratulations, mission complete!")
        else:
            print("You lost!")

class Round(models.Round):

    def start_round(self):
        for player_idx in self.game.state.player_order:
            self.game.state.current_player_idx = player_idx
            player = self.game.players[player_idx]
            player.play_round_start_actions(self.game.state)

    def end_round(self):
        for player_idx in self.game.state.player_order:
            self.game.state.current_player_idx = player_idx
            player = self.game.players[player_idx]
            player.play_round_end_actions(self.game.state)

        # check if a task was fullfilled
        self.game.state.task_complete()
        # promote winner to captain
        leader = self.game.state.fold.leader()
        self.game.state.promote_to_captain(leader)
        # discard fold
        self.game.state.discard.append(self.game.state.fold)
        # new empty fold
        self.game.state.fold = Fold()

    def play(self):
        self.start_round()

        # each player plays
        for player_idx in self.game.state.player_order:
            self.game.state.current_player_idx = player_idx
            player = self.game.players[player_idx]
            player.play_round_regular_actions(self.game.state)
            for player_idx in self.game.state.player_order:
                self.game.state.current_player_idx = player_idx
                player = self.game.players[player_idx]
                player.play_round_interrupt_actions(self.game.state)
                
        self.end_round()

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
        if game_state.mission_number == 4:
            self.special_mission_4(game_state)
        
    def special_mission_4(self, game_state):
        player_idx = game_state.current_player_idx
        if game_state.player_order.index(player_idx) == 0: # captain
            crewmates = game_state.player_order[1:]
            name_list = [game_state.player_names[i] for i in crewmates]
            _,choice = self.menu_select(name_list)
            game_state.is_sick = crewmates[choice]
            print("{} is sick".format(game_state.player_names[game_state.is_sick]))
        else: # crewmates
            _,game_state.player_state[player_idx] = self.menu_select(["good","bad"])
            print(game_state.player_names[player_idx] + " is feeling " + game_state.player_state[player_idx])

    def play_card(self,game_state):
        # select admissible cards
        player_idx = game_state.current_player_idx
        cards_list = game_state.admissible_cards()
        _,card_to_play = self.menu_select(cards_list)
        game_state.play_card(player_idx,card_to_play)
        print("{} played {}".format(game_state.player_names[player_idx], card_to_play))

class Bot(models.RandomBot):

    def register_setup_actions(self):
        # define a list of functions that take the game as input
        self.setup_actions = [self.do_setup]

    def register_round_regular_actions(self):
        self.round_regular_actions = [self.play_card]
    
    def special_mission_4(self, game_state):
        player_idx = game_state.current_player_idx
        if game_state.player_order.index(player_idx) == 0: # captain
            crewmates = game_state.player_order[1:]
            game_state.is_sick = random.choice(crewmates)
            print("{} is sick".format(game_state.player_names[game_state.is_sick]))
        else: # crewmates
            game_state.player_state[player_idx] = random.choice(["good","bad"])
            print(game_state.player_names[player_idx] + " is feeling " + game_state.player_state[player_idx])

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
        cards_list = game_state.admissible_cards()
        card_to_play = random.choice(cards_list)
        game_state.play_card(player_idx,card_to_play)
        print("{} played {}".format(game_state.player_names[player_idx], card_to_play))

class SmartBot(models.Player):
    #TODO
    pass
