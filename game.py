from models import *
import random

CARD_COLORS = ['green', 'yellow', 'blue', 'pink']
MISSION_DATABASE = [
    [1,[]],
    [2,[]],
    [2,[1,2]],
    [3,[]],
    [0,[-1]]
]


card_deck = [Card(color, number) for color in CARD_COLORS for number in range(1, 10)] + [Card('black', number) for number in range(1, 5)]
mission_deck = [Mission(color, number) for color in CARD_COLORS for number in range(1, 10)]
random.shuffle(mission_deck)

players = [
    Player('Marie'),
    Player('Fabiana'),
    Player('Martin'),
    Player('Lucas'),
    Player('Pierrick')
]

captain_idx = draw_cards(card_deck, players)
# reorder to make captain first
players = [players[(idx + captain_idx) % len(players)] for idx in range(len(players))]

draw_mission(mission_deck,players,0)

print('Starting game with')
for player in players:
    print(player)

print('Lets play!')
turn = Turn(players)
turn.play()





