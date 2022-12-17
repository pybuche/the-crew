import gymnasium
import numpy as np
from gymnasium.spaces import Discrete, Dict, MultiDiscrete
from pettingzoo import AECEnv
from pettingzoo.utils import agent_selector, wrappers
from the_crew import *

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

    def __str__(self):
        return "Agent_{}".format(self.name)

def env():
    env = raw_env()
    env = wrappers.TerminateIllegalWrapper(env, illegal_reward=-1)
    env = wrappers.AssertOutOfBoundsWrapper(env)
    env = wrappers.OrderEnforcingWrapper(env)
    return env

class raw_env(AECEnv):
    def __init__(self):
        super().__init__()

        self.agents = ["player_" + str(r) for r in range(5)]

        # MultiDiscrete: A list of possible actions, where each timestep only 
        # one action of each discrete set can be used.
        self.action_spaces = {agent: Discrete(185) for agent in self.agents}
        self.observation_spaces = {
            agent: Dict( 
                {
                    "observation" : MultiDiscrete([6]*40 # players (0, p1-p5)
                        + [3]*40  # location (hand,fold,discard)
                        + [41]*40 # order played
                        + [7]*36 # tasks (0, drawn, p1-p5)
                        + [37]*10 # modifiers (0, task card #)
                        + [41]*5 # com card (0, card number)
                        + [4]*5 # com value (0, small,only,big)
                        + [2]*5 # com allowed (true,false)
                        + [5]), # captain 
                    "action_mask" : Discrete(185)
                }
            )
            for agent in self.agents
        }

    def observe(self, agent):
        cur_player = self.agents.index(agent)

        observation = None

        legal_moves = self._legal_moves() if agent == self.agent_selection else []

        action_mask = np.zeros(185, "int8")
        for i in legal_moves:
             action_mask[i] = 1

        return {"observation": observation, "action_mask": action_mask}
    
    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def _legal_moves(self):
        return [] #TODO ask game to give a list of 185 values with legal actions

    def step(self,action):
        if (
            self.truncations[self.agent_selection]
            or self.terminations[self.agent_selection]
        ):
            return self._was_dead_step(action)

        # interact with game to do the action via game.step(agent, action)
        # self.agent_selection contains the current agent
         
        #TODO change agent order with self._agent_selector.reinit(new_agent_order)
        # self._agent_selector.is_last returns True if last agent in turn 
        
        next_agent = self._agent_selector.next()
        winner = self.check_for_winner()

        # check if there is a winner
        if winner: #TODO change this so that all agents get a big reward 
            self.rewards[self.agent_selection] += 1  # change that to every agent
            #self.rewards[next_agent] -= 1 # change that
            self.terminations = {i: True for i in self.agents}
        else:
            # no winner yet
            self.agent_selection = next_agent

        self._accumulate_rewards()

    def reset(self):
        self.agents = self.possible_agents[:]
        self.rewards = {i: 0 for i in self.agents}
        self._cumulative_rewards = {name: 0 for name in self.agents}
        self.terminations = {i: False for i in self.agents}
        self.truncations = {i: False for i in self.agents}
        self.infos = {i: {} for i in self.agents}
        self._agent_selector = agent_selector(self.agents)
        self.agent_selection = self._agent_selector.reset()


    def render(self):
        pass

    def close(self):
        pass