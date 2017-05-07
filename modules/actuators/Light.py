
class Light(object):
    """docstring for Light"""
    def __init__(self, pwm):
        super(Light, self).__init__()
        self.pwm = pwm
        print("light initialized")