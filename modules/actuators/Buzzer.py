import time

class Buzzer(object):
    """docstring for Buzzer"""
    def __init__(self):
        super(Buzzer, self).__init__()
        self.lastBuzz = 0
        print("buzzer initialized")

    def buzz(self, ignorePeriod):
        if ignorePeriod == 0:
            print("Buzzer is buzzing...")
    	elif time.time() - self.lastBuzz > ignorePeriod:
    		# print("Buzzer is buzzing...")
    		self.lastBuzz = time.time()
    	else:
    		# print("Buzzer: still in the middle of the last buzz")
            pass