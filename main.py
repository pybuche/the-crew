from models import *

players = [
    Bot("Bot0"),
    Bot("Bot1"),
    Bot("Bot2"),
    Bot("Bot3"),
    Human("Human")
]

g = Game(players)
g.play()