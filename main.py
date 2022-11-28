from the_crew import *
from network import *

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

# 3 bots
players = [
    Bot("Lucas"),
    Bot("Pierrick"),
    Bot("Fabiana")
]

Game = TheCrew(players)
Game.play()

# 4 bots
players = [
    Bot("Lucas"),
    Bot("Pierrick"),
    Bot("Fabiana"),
    Bot("Marie")
]

Game = TheCrew(players,0)
Game.play()

# network

# server
from the_crew import *
from network import *
players = [
    Bot("Lucas"),
    Bot("Pierrick"),
    Bot("Fabiana"),
    PlayerServer("Marie",5007)
]
Game = TheCrew(players,0)
Game.play()

# client
from the_crew import *
from network import *
player = Human("Marie")
PC = PlayerClient("localhost",5007,player,debug=True)