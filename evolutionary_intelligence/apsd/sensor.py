class Sensor:
    """
    sensor object

    :param
        sensorId (int)   - id (starts at 0 and smaller ids more important for coverage)

        xPos (int)       - location's x position
        yPos (int)       - location's y position

        priority (float) - priority value which is coming from clusters
    """

    def __init__(self, sensorId, xPos, yPos, priority=0.0):
        self.sensorId = sensorId

        self.xPos = xPos
        self.yPos = yPos

        self.priority = priority

        self.connected = []

    def __str__(self):
        return 'Sensor: ',\
               'id =', self.sensorId, 'priority =', self.priority,\
               'xPos =', self.xPos, 'yPos =', self.yPos
