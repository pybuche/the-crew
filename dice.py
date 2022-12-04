import random

class Dice:
    def __init__(self,num_faces=6,faces_labels=None):
        self.num_faces = num_faces
        self.faces_labels = faces_labels

    def roll(self):
        return random.choice(range(self.num_faces))


