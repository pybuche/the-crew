from the_crew import *

players = [
    Bot("Lucas"),
    Bot("Pierrick"),
    Bot("Fabiana"),
    Bot("Marie"),
    Human("Martin")
]

Game = TheCrew(players)
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