def simulated_annealing(self):
    """
    finding better solution for deployment with simulated annealing optimization method

    :param
        temperature (float)         - SA steps starting value
        coolingRate (float)         - each step temperature multiplied by coolingRate to reach absoluteTemperature
        absoluteTemperature (float) - SA steps ending value

        moveX (int)                 - random movement value for x coordinate (random sensor move at each SA step)
        moveY (int)                 - random movement value for y coordinate (random sensor move at each SA step)

        maxPriority (float)         - update maxPriority if current deployment is better
        delta (float)               - difference between current deployment p

    :return
        deployed sensors which are optimized their priorities and locations
    """

    print "-> Simulated Annealing Optimization"
    iterCnt = 0

    temperature = 0.3
    coolingRate = 0.9995
    absoluteTemperature = 0.05

    self.find_connected_component()
    maxPriority = sum([sensor.priority for sensor in self.sensors]) / float(self.calc_connected_component())
    radius = self.cfg.radius

    while temperature > absoluteTemperature:
        sensor = random.choice(self.sensors)
        tempSensorPriority = sensor.priority

        moveX = int(round(3 * temperature * radius * random.uniform(-1.0, 1.0)))
        moveY = int(round(3 * temperature * radius * random.uniform(-1.0, 1.0)))

        log_message = "SensorOld" + " " + str(sensor.sensorId) + " " + \
                      str(sensor.xPos) + " " + str(sensor.yPos) + " " + str(sensor.priority)
        # remove sensor
        self.uncover(sensor.xPos, sensor.yPos, sensor.sensorId)

        # find connected sensors
        connectedSensors = self.find_connected_sensors(sensor.xPos, sensor.yPos, self.sensors[(sensor.sensorId+1):])

        sensor.xPos += moveX
        sensor.yPos += moveY

        newConnected = self.find_connected_sensors(sensor.xPos, sensor.yPos, self.sensors[(sensor.sensorId+1):])
        # connection
        for sc in sensor.connected:
            sc.connected.remove(sensor)
        sensor.connected = []
        newConnection = self.find_connected_sensors(sensor.xPos, sensor.yPos, self.sensors)
        for unconnected in newConnection:
            sensor.connected.append(unconnected)
            unconnected.connected.append(sensor)

        for conSensor in newConnected:
            if conSensor not in connectedSensors:
                connectedSensors.append(conSensor)

        connectedSensors = sorted(connectedSensors, key=lambda s: s.sensorId)

        # add sensor and calculate priority
        sensor.priority, c = self.cover_and_priority(sensor.xPos, sensor.yPos, sensor.sensorId)

        # update priority for connected sensors
        tempConnectedPriorities = []
        for conSensor in connectedSensors:
            tempConnectedPriorities.append(conSensor.priority)
            conSensor.priority, c = self.cover_and_priority(conSensor.xPos, conSensor.yPos, conSensor.sensorId)

        newPriority = sum([s.priority for s in self.sensors]) / float(self.calc_connected_component())

        delta = newPriority - maxPriority

        if delta >= 0 or (math.exp(float(delta)*15 / temperature) > random.random()):
            maxPriority = newPriority
        else:
            self.uncover(sensor.xPos, sensor.yPos, sensor.sensorId)
            sensor.xPos -= moveX
            sensor.yPos -= moveY
            sensor.priority = tempSensorPriority

            self.cover(sensor.xPos, sensor.yPos, sensor.sensorId)

            for i, conSensor in enumerate(connectedSensors):
                conSensor.priority = tempConnectedPriorities[i]

                self.cover(conSensor.xPos, conSensor.yPos, conSensor.sensorId)

        temperature *= coolingRate
        iterCnt += 1

        log_message += "\nSensorNew" + " " + str(sensor.sensorId) + " " + \
                       str(sensor.xPos) + " " + str(sensor.yPos) + " " + str(sensor.priority)

        log_message += "\nMaxPriority" + " " + str(maxPriority) + " " + "Temperature" + "" + str(temperature)

        self.notify(log_message)

    print "iteration:", iterCnt
    print "Priority:", maxPriority,

    return maxPriority

def find_connected_component(self):
    edgeSqr = self.cfg.gridEdge ** 2

    for i in range(len(self.sensors)-1):
        for j in range(i+1, len(self.sensors)):
            dist = (self.sensors[i].xPos - self.sensors[j].xPos) ** 2 + (self.sensors[i].yPos - self.sensors[j].yPos) ** 2

            if dist <= edgeSqr:
                self.sensors[i].connected.append(self.sensors[j])
                self.sensors[j].connected.append(self.sensors[i])

def calc_connected_component(self):
    unchecked = copy.deepcopy(self.sensors)
    componentCount = 0

    while unchecked:
        willCheck = unchecked[0].connected
        checked = [unchecked[0]]

        while willCheck:
            for i in willCheck[0].connected:
                if i not in checked and i not in willCheck:
                    willCheck.append(i)
            checked.append(willCheck[0])
            checked = list(set(checked))
            willCheck.remove(willCheck[0])

        for c in checked:
            unchecked.remove(c)
        componentCount += 1

    return componentCount