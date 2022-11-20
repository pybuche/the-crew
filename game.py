from models import *


CARD_COLORS = ['green', 'yellow', 'blue', 'pink']
MISSION_DECK = [Card(color, number) for color in CARD_COLORS for number in range(1, 10)]

PLAYERS = [
    Player('Marie'),
    Player('Fabiana'),
    Player('Martin'),
    Player('Lucas'),
    Player('Pierrick')
]

def draw_cards(players):
    card_deck = [Card(color, number) for color in CARD_COLORS for number in range(1, 10)] + [Card('black', number) for number in range(1, 5)]
    captain_index = 0
    random.shuffle(card_deck)
    while len(card_deck) > 0:
        for (index, player) in enumerate(players):
            card = card_deck.pop()
            # print('giving {} to {}'.format(card, player))
            if card.color == 'black' and card.number == 4:
                captain_index = index
            player.add_card(card)
    return captain_index

class Game:
    def __init__(self):
        self.players = PLAYERS
        self.mission_deck = [Card(color, number) for color in CARD_COLORS for number in range(1, 10)]

    def reorder_players(self, captain_index):
        self.players = [self.players[(idx + captain_index) % len(self.players)] for idx in range(len(self.players))]

    def play_mission(self, mission):
        turn_index = 0
        winner_index = None
        captain_index = 0
        mission_completed = False
        has_won_mission = False
        while not mission_completed:
            turn_index += 1
            turn = Turn(self.players, turn_index, mission)
            winner_index, mission_completed = turn.play(captain_index)

            print('-----------------------')
            print('Winner is {}'.format(self.players[winner_index].name))
            self.reorder_players(winner_index)

            if mission_completed:
                has_won_mission = (captain_index == winner_index)
                break

            captain_index = (captain_index - winner_index) % 5
            print('Captain is still {}'.format(self.players[captain_index].name))

        return has_won_mission


    def play(self, counter = 1):
        # Players have no cards in hand
        for player in self.players:
            player.cards = []

        # Draw cards
        captain_index = draw_cards(self.players)
        self.reorder_players(captain_index)
        print('##########################')
        print('Starting game with')
        for player in self.players:
            print(player)
        print('##########################')

        print('{} is the captain!'.format(self.players[0].name))
        print('##########################')

        print('Let\'s play!')
        print('##########################')
        print('Selecting mission')
        random.shuffle(self.mission_deck)
        mission = self.mission_deck.pop(0)
        self.mission_deck.append(mission)

        print('Playing mission {}'.format(mission))
        has_won_mission = self.play_mission(mission)

        print('##########################')
        if not has_won_mission:
            print('GAME OVER')
            print('##########################')
            return self.play(counter + 1)

        print('YOU WON MISSION {} AFTER {} tries'.format(mission, counter))
        print('##########################')
        return counter


tries = 0
min = 0
max = 0
values = []
for i in range(0, 10000):
    game = Game()
    counter = game.play()
    values.append(counter)
    tries += counter
    min = counter if counter < min or i == 0 else min
    max = counter if counter > max else max

print(tries / 10000, min, max)
print(values)
