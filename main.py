from the_crew import *

players = [
    Bot("Lucas"),
    Bot("Pierrick"),
    Bot("Fabiana"),
    Bot("Marie"),
    Human("Martin")
]

State = GameState(players) 
Game = TheCrew(State)
Game.play()

players = [
    Bot("Lucas"),
    Bot("Pierrick"),
    Bot("Fabiana"),
    Bot("Marie"),
    Bot("Martin")
]

State = GameState(players) 
Game = TheCrew(State)
Game.play()