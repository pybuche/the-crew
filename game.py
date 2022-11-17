from models import *
from utils import draw_cards


CARD_COLORS = ['green', 'yellow', 'blue', 'pink']

MISSION_DECK = [Card(color, number) for color in CARD_COLORS for number in range(1, 10)]
CARD_DECK = MISSION_DECK + [Card('black', number) for number in range(1, 5)]


PLAYERS = [
    Player('Marie'),
    Player('Fabiana'),
    Player('Martin'),
    Player('Lucas'),
    Player('Pierrick')
]

class Game:
    def __init__(self):
        self.players = PLAYERS
        self.card_deck = CARD_DECK
        self.mission_deck = MISSION_DECK

    def reorder_players(self, captain_index):
        self.players = [self.players[(idx + captain_index) % len(self.players)] for idx in range(len(self.players))]

    def play_mission(self, mission):
        turn_index = 0
        winner_index = None
        captain_index = 0
        mission_completed = False
        while not mission_completed:
            turn_index += 1
            turn = Turn(self.players, turn_index, mission)
            winner_index, mission_completed = turn.play()

            print('-----------------------')
            print('Winner is {}'.format(self.players[winner_index].name))
            self.reorder_players(winner_index)

            print('Mission {} completed: {}'.format(mission, mission_completed))

            if mission_completed:
                print('##########################')
                if captain_index == winner_index:
                    print('YOU WON')
                else:
                    print('GAME OVER')
                print('##########################')
                return

            captain_index = (captain_index - winner_index) % 5
            print('Captain is still {}'.format(self.players[captain_index].name))


    def play(self):
        # Draw cards
        captain_index = draw_cards(self.card_deck, self.players)
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
        self.mission_deck = self.mission_deck.append(mission)

        print('Playing mission {}'.format(mission))
        self.play_mission(mission)
        print('##########################')


game = Game()
game.play()


