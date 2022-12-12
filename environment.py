import gym
from gym import spaces
from the_crew import *
from models import Player
import time

# TODO use petting zoo for MARL instead of gym

class Agent(Player):
    def __init__(self,name):
        self.game_request = False
        self.observation = None
        self.reward = 0

        CARD_COLORS = ['green', 'yellow', 'blue', 'pink']
        TRUMP_COLOR = 'black'
        deck = [CommCard(color, number, TRUMP_COLOR) for color in CARD_COLORS for number in range(1, 10)] \
            + [CommCard(TRUMP_COLOR, number, TRUMP_COLOR) for number in range(1, 5)]
        task_deck = [TaskCard(color, number) for color in CARD_COLORS for number in range(1, 10)]
        comm_deck = [CommCard(color, number, TRUMP_COLOR, comm_idx) for comm_idx in range(3) for color in CARD_COLORS for number in range(1, 10) ]

        self.taskdraw_dict = {idx: taskcard for (idx, taskcard) in enumerate(task_deck)}
        self.playcard_dict = {idx+36: card for (idx, card) in enumerate(deck)}
        self.comm_dict = {idx+77: card for (idx, card) in enumerate(comm_deck)}

        super().__init__('Agent ' + name)

    def step(self,game_state,action):
        
        if 0 <= action < 36: # draw task card
            if not game_state.current_game_phase == 0:
                # invalid action 
                return False
            
            player_idx = game_state.current_player_idx
            card = self.taskdraw_dict[action]
            if card in game_state.drawn_tasks: # valid action
                task_idx = game_state.drawn_tasks.index(card)
                game_state.hand_tasks[player_idx].append(game_state.drawn_tasks[task_idx])
                game_state.drawn_tasks.pop(task_idx)
                return True
            else: # invalid task card
                return False
                 
        elif 36 <= action < 76: # play a card
            if not game_state.current_game_phase == 2:
                # invalid action 
                return False

            player_idx = game_state.current_player_idx
            card = self.playcard_dict[action]

            if not card in game_state.hand_cards[player_idx]: #invalid action
                return False

            # get actual card from the game 
            idx = game_state.hand_cards[player_idx].index(card)
            gamecard = game_state.hand_cards[player_idx][idx]

            playable_cards = game_state.admissible_cards()
            if not card in playable_cards: # invalid card 
                return False

            game_state.play_card(player_idx,gamecard) 
            return True

        elif 76 <= action < 185: # communicate
            if not game_state.current_game_phase == 1: # invalid action
                return False

            player_idx = game_state.current_player_idx
            if not game_state.radio_tokens[player_idx]: # invalid action 
                return False

            if action == 76: # no communication
                return True
            else:
                card = self.comm_dict[action]
                if not card in game_state.hand_cards[player_idx]: #invalid action
                    return False

                # get actual card from the game 
                idx = game_state.hand_cards[player_idx].index(card)
                gamecard = game_state.hand_cards[player_idx][idx]

                valid_comm = game_state.admissible_communication(gamecard)
                if card.comm_idx != valid_comm : #invalid action
                    return False

                game_state.communicate(gamecard,card.comm_idx)

    def __repr__(self):
        return "Agent_{}".format(self.name)

class Environment(gym.Env):
    def __init__(self):
        super().__init__()
        self.agent = Agent()
        # MultiDiscrete: A list of possible actions, where each timestep only 
        # one action of each discrete set can be used.
        self.action_space = spaces.MultiDiscrete([36,40,36*3+1])

        self.observation_space = spaces.MultiDiscrete([6]*40 # players (0, p1-p5)
            + [3]*40  # location (hand,fold,discard)
            + [41]*40 # order played
            + [7]*36 # tasks (0, drawn, p1-p5)
            + [37]*10 # modifiers (0, task card #)
            + [41]*5 # com card (0, card number)
            + [4]*5 # com value (0, small,only,big)
            + [2]*5 # com allowed (true,false)
            + [5]) # captain 
    
    def step(self,action):
        # step through the environment, interact with the game
        return self.agent.step(action)

    def reset(self):
        # start a new game
        players = [
            Agent("Smith"),
            Bot("Brown"),
            Bot("Jones"),
            Bot("Johnson"),
            Bot("Thompson")
        ]
        self.game = TheCrew(players,0)

        return observation  # reward, done, info can't be included

    def render(self):
        pass

    def close(self):
        pass