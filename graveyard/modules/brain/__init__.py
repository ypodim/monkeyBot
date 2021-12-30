from mainAI import AI

class Brain(object):
    """docstring for Brain"""
    def __init__(self, sensors, actuators):
        super(Brain, self).__init__()
        self.AI = AI(sensors, actuators)
        print("brain initialized")

    def think(self):
        self.AI.think()

