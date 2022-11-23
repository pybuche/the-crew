from the_crew import *

# with human player
players = [
    Bot("Lucas"),
    Bot("Pierrick"),
    Bot("Fabiana"),
    Bot("Marie"),
    Human("Martin")
]

mission_number = 2
Game = TheCrew(players,mission_number)
Game.play()

# with bots only
players = [
    Bot("Lucas"),
    Bot("Pierrick"),
    Bot("Fabiana"),
    Bot("Marie"),
    Bot("Martin")
]

Game = TheCrew(players)
Game.play()