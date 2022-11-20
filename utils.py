import random

MISSION_DATABASE = [
    [1,[]],
    [2,[]],
    [2,[1,2]],
    [3,[]],
    [0,[-1]]
]

def draw_mission(mission_deck, players, mission_number):
    mission = MISSION_DATABASE[mission_number]
    if mission[0] == 0:
        # special mission
        modifier = mission[1]
        if modifier[0] == -1: # first special mission
            pass
        elif modifier[0] == -2: # second special mission
            pass
    else:
        # regular mission
        number_of_cards = mission[0]
        modifiers = mission[1]
        mission_list = mission_deck[0:number_of_cards]
        # put the mission back at the end of the deck
        mission_deck = [mission_deck[(idx + number_of_cards) % len(mission_deck)] for idx in range(len(mission_deck))]
        # deal missions to players starting with captain
