from models import *
import random

CARD_COLORS = ['green', 'yellow', 'blue', 'pink']

def draw_cards(cards, players):
    random.shuffle(cards)
    while len(cards) > 0:
        for player in players:
            card = cards.pop()
            print('giving {} to {}'.format(card, player))
            player.add_card(card)


card_set = [Card(color, number) for color in CARD_COLORS for number in range(1, 10)] + [Card('black', number) for number in range(1, 5)]
players = [
    Player('Marie'),
    Player('Fabiana'),
    Player('Martin'),
    Player('Lucas'),
    Player('Pierrick')
]

draw_cards(card_set, players)

print('Starting game with')
for player in players:
    print(player)

print('Lets play!')
turn = Turn(players)
turn.play()





