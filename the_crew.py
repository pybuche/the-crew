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
        # TODO get rid of object player in game.state, use index instead
        # this is necessary for the serialization of game.state since 
        # players could contain sockets that are non pickable

        self.state.num_players = len(players)
        self.state.hand_cards = {p:[] for p in players}
        self.state.hand_tasks = {p:[] for p in players}
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

        if self.state.mission_number == 4:
            # additional state variables
            self.state.player_state = {}
            self.state.is_sick = None
        
        print(self.state.mission_description)
        super().__init__(players)

    def end_round(self):
        # check if a task was fullfilled
        self.task_complete()
        # promote winner to captain
        self.promote_to_captain(self.state.fold.leader())
        # discard fold
        self.state.discard.append(self.state.fold)
        # new empty fold
        self.state.fold = Fold()

    def task_complete(self):
        # check if a task or more was done in the fold
        for player,card in self.state.fold.content:
            if player == self.state.fold.leader():
                for task in self.state.hand_tasks[player]:
                    if task.color == card.color and task.number == card.number:
                        print(str(player) + ' completed task ' + str(task))
                        self.state.hand_tasks[player].remove(task)
                        self.state.resolved_tasks.append(task)
                        # TODO: the rule states that if two tasks are done in 
                        # the same fold and they have modifiers (like 1 and 2)
                        # they are considered solved in the right order no 
                        # matter the order of those cards in the fold
                        

    def admissible_cards(self,player):
        if self.state.fold.isempty():
            # first to play, you can play anything
            return [cards for cards in self.state.hand_cards[player]]
        else:
            # if you have the required color, you must play that
            required_color = [cards for cards in self.state.hand_cards[player] if cards.color == self.state.fold.color()]
            if required_color:
                return required_color
            else:
                # if not you need to cut
                trumps = [cards for cards in self.state.hand_cards[player] if cards.color == 'black']
                if trumps:
                    return trumps
                else:
                    # you have nothing, play whatever
                    return [cards for cards in self.state.hand_cards[player]]

    def play_card(self,player,card):
        if card in self.admissible_cards(player):
            self.state.hand_cards[player].remove(card)
            self.state.fold.add_card(player,card)
            print(str(player) + ' played ' + str(card))
        else:
            print('You cannot play this card!')

    def promote_to_captain(self,player):
        print(str(player) + ' is the captain!')
        player_idx = self.players.index(player)
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
            for player in self.players: 
                if deck:
                    card = deck.pop()
                    if card.color == 'black' and card.number == 4:
                        captain = player
                    self.state.hand_cards[player].append(card)
   
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
        for p in self.players:
            if not self.state.hand_cards[p]:
                empty_hands = True
            if self.state.hand_tasks[p]:
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
            for p in self.players[1:]:
                p.play_setup_actions(self)
            # then the captain
            self.players[0].play_setup_actions(self)
        else:
            for p in self.players:
                p.play_setup_actions(self)

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
        for p in self.players:
            reprstr = reprstr + str(p) \
                + '\n\tHand: ' + ','.join([str(card) for card in self.state.hand_cards[p]]) \
                + '\n\tTasks: ' + ','.join([str(card) for card in self.state.hand_tasks[p]]) \
                + '\n'  
        reprstr = reprstr + ','.join([str(task) for task in self.self.state.drawn_tasks])
        return reprstr

class Round(models.Round):
    def end_round(self):
        super().end_round()
        self.game.end_round()

class Human(models.Human):
    def register_setup_actions(self):
        # define a list of functions that take the game as input
        self.setup_actions = [self.do_setup]

    def register_round_regular_actions(self):
        self.round_regular_actions = [self.play_card]

    def do_setup(self, game):
        if game.self.state.drawn_tasks:
            index,mission = self.menu_select(game.self.state.drawn_tasks)
            game.hand_tasks[self].append(mission)
            game.self.state.drawn_tasks.pop(index)
        if game.mission_number == 4:
            self.special_mission_4(game)
        
    def special_mission_4(self, game):
        if self == game.players[0]: # captain
            for p in game.players[1:]:
                _,game.is_sick = self.menu_select(game.players[1:])
                print("{} is sick".format(game.is_sick))
        else: # crewmates
            _,game.player_state[self] = self.menu_select(["good","bad"])
            print("{} is feeling ".format(self) + game.player_state[self])

    def play_card(self,game):
        # select admissible cards
        admissible_cards = game.admissible_cards(self)
        _,card_to_play = self.menu_select(admissible_cards)
        game.play_card(self,card_to_play)

class Bot(models.RandomBot):

    def register_setup_actions(self):
        # define a list of functions that take the game as input
        self.setup_actions = [self.do_setup]

    def register_round_regular_actions(self):
        self.round_regular_actions = [self.play_card]
    
    def special_mission_4(self, game):
        if self == game.players[0]: # captain
            game.is_sick = random.choice(game.players[1:])
            print("{} is sick".format(game.is_sick))
        else: # crewmates
            game.player_state[self] = random.choice(["good","bad"])
            print("{} is feeling ".format(self) + game.player_state[self])

    def do_setup(self,game):
        if game.self.state.drawn_tasks:
            # select the first card
            game.hand_tasks[self].append(game.self.state.drawn_tasks[0])
            game.self.state.drawn_tasks.pop(0)
        if game.mission_number == 4:
            self.special_mission_4(game)

    def play_card(self,game):
        # select admissible cards
        admissible_cards = game.admissible_cards(self)
        card_to_play = random.choice(admissible_cards)
        game.play_card(self,card_to_play)

class SmartBot(models.Player):
    #TODO
    pass
