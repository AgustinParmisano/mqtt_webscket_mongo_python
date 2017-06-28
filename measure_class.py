class Measure(object):
    """docstring for Measure."""
    def __init__(self, potencia, tension, timedata, state):
        super(Measure, self).__init__()
        self.potencia = potencia
        self.tension = tension
        self.timedata = timedata
        self.state = state

    def set_potencia(self, potencia):
        self.potencia = potencia

    def set_tension(self, tension):
        self.tension = tension

    def set_timedata(self, timedata):
        self.timedata = timedata

    def set_state(self, state):
        self.state = state

    def get_potencia(self):
        return self.potencia

    def get_tension(self):
        return self.tension

    def get_timedata(self):
        return self.timedata

    def get_state(self):
        return self.state
