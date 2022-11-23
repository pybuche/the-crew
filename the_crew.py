import models 
import random
import json
from cards import *

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

        self.hand_cards = {p:[] for p in players}
        self.hand_tasks = {p:[] for p in players}
        self.communication = {p:[] for p in players}
        self.has_communicated = {p:False for p in players}
        self.discard = []
        self.fold = Fold()

        # tasks
        self.mission_number = mission_number
        with open('the_crew_missions.json','r') as fp:
            self.mission_list = json.load(fp)
        self.num_tasks = self.mission_list[mission_number][0]
        self.modifiers = self.mission_list[mission_number][1]
        self.mission_description = self.mission_list[mission_number][2]
        self.special_mission = []; # TODO populate this
        self.drawn_tasks = []
        self.resolved_tasks = []
        self.win = False
        
        print(self.mission_description)
        super().__init__(players)

    def end_round(self):
        # check if a task was fullfilled
        self.task_complete()
        # promote winner to captain
        self.promote_to_captain(self.fold.leader())
        # discard fold
        self.discard.append(self.fold)
        # new empty fold
        self.fold = Fold()

    def task_complete(self):
        # check if a task was done in the fold
        for player,card in self.fold.content:
            if player == self.fold.leader():
                for task in self.hand_tasks[player]:
                    if task.color == card.color and task.number == card.number:
                        # pop task if complete
                        print(str(player) + ' completed task ' + str(task))
                        self.hand_tasks[player].remove(task)
                        self.resolved_tasks.append(task)
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
        TRUMP_COLOR = 'black'

        # create and shuffle deck of cards
        deck = [Card(color, number, TRUMP_COLOR) for color in CARD_COLORS for number in range(1, 10)] \
            + [Card(TRUMP_COLOR, number, TRUMP_COLOR) for number in range(1, 5)]
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

        # Draw tasks
        task_deck = [TaskCard(color, number) for color in CARD_COLORS for number in range(1, 10)]
        random.shuffle(task_deck)

        for idx in range(self.num_tasks):
            task = task_deck.pop(0)
            if self.modifiers:
                task.modifier = self.modifiers[idx]
            self.drawn_tasks.append(task)

        print(self)

    def failed_mission(self):

        if self.mission_number in self.special_mission:
            # implement special mission rules here 
        else:
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

        #TODO implement his for special missions
        if self.failed_mission():
            return True

        empty_hands = True
        tasks_done = True
        for p in self.players:
            if self.hand_cards[p]:
                empty_hands = False
            if self.hand_tasks[p]:
                tasks_done = False

        if tasks_done:
            self.win = True
            return True
        
        return empty_hands

    def play(self):
        print('Let\'s play!')
        
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

    def end_game(self):
        if self.win:
            print("Congratulations, mission complete!")
        else:
            print("You lost!")

    def __repr__(self):
        reprstr = ''
        for p in self.players:
            reprstr = reprstr + str(p) \
                + '\n\tHand: ' + ','.join([str(card) for card in self.hand_cards[p]]) \
                + '\n\tTasks: ' + ','.join([str(card) for card in self.hand_tasks[p]]) \
                + '\n'  
        reprstr = reprstr + ','.join([str(task) for task in self.drawn_tasks])
        return reprstr

class Round(models.Round):
    def end_round(self):
        super().end_round()
        self.game.end_round()

class Human(models.Human):
    def register_setup_actions(self):
        # define a list of functions that take the game as input
        self.setup_actions = [self.select_task_card]

    def register_round_regular_actions(self):
        self.round_regular_actions = [self.play_card]

    def select_task_card(self, game):
        if game.drawn_tasks:
            index,mission = self.menu_select(game.drawn_tasks)
            game.hand_tasks[self].append(mission)
            game.drawn_tasks.pop(index)

    def play_card(self,game):
        # select admissible cards
        admissible_cards = game.admissible_cards(self)
        _,card_to_play = self.menu_select(admissible_cards)
        game.play_card(self,card_to_play)

class Bot(models.RandomBot):

    def register_setup_actions(self):
        # define a list of functions that take the game as input
        self.setup_actions = [self.select_task_card]

    def register_round_regular_actions(self):
        self.round_regular_actions = [self.play_card]
    
    def select_task_card(self,game):
        if game.drawn_tasks:
            # select the first card
            game.hand_tasks[self].append(game.drawn_tasks[0])
            game.drawn_tasks.pop(0)

    def play_card(self,game):
        # select admissible cards
        admissible_cards = game.admissible_cards(self)
        card_to_play = random.choice(admissible_cards)
        game.play_card(self,card_to_play)

class SmartBot(models.Player):
    #TODO
    pass
