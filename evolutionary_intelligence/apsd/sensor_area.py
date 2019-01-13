import math
import random
import colorsys
import copy

from grid import Grid
from sensor import Sensor

import image_handler
from subject import Subject

import array
import random
import json

import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools


class SensorArea(Subject):

    def __init__(self, cfg):
        """
        initializing sensor area, deployment sensors and optimization for deployment
        this class uses observer pattern

        :param
            sensors (sensor list) - list of sensors will deploy to the sensor area

            grids (grid list)     - grids on the sensor area
            pixels (pixel matrix) - matrix for each pixel's color value information

            cfg (Config)          - Config instance for global parameters
        """
        Subject.__init__(self)
        
        self.sensors = []

        self.grids = []
        self.pixels = []

        self.cfg = cfg

        self.initialize_grids()

    # HELPER FUNCTIONS
    def calc_avg_std(self, colors):
        """
        find average values and standard deviation values for color values list
        """

        average = []
        standardDeviation = []

        for c in colors:
            avg = sum(c) / float(len(c))

            variance = [(x - avg) ** 2 for x in c]
            stdDev = math.sqrt(sum(variance) / len(variance))

            average.append(avg)
            standardDeviation.append(stdDev)

        return average, standardDeviation

    def collect_color_values(self, c1, c2, c3, x, y):
        """
        get color values for pixel which is in given coordinates
        """

        pass

        # pixel = self.pixels[x, y]

        # c1.append(pixel[0])
        # c2.append(pixel[1])
        # c3.append(pixel[2])

        # pixel = self.convertedPixels[x][y]

    def find_cluster_and_priority(self, colorAvg, colorStdDev, sizeRatio):
        """
        finding cluster and priority value with given color information

        :param
            colorAvg (float list)     - average values for each color
            colorStdDev (float list)  - standard deviation values for each color
            sizeRatio (float)         - coverage ratio for sensor or grid

        :return:
            priority (float)          - priority value (clusterPriority * sizeRatio)
            nearestClusterIndex (int) - cluster number
        """
        colorAvgStd = colorAvg + colorStdDev

        # find cluster, then priority value
        nearestClusterIndex = self.cfg.clusteringMethod.find_nearest_cluster(colorAvgStd)
        priority = self.cfg.clusterPriorities[nearestClusterIndex] * sizeRatio

        return priority, nearestClusterIndex

    # IMAGE LOADING FUNCTIONS
    def convert_color_space(self):
        """
        converting rgb color space to hsv fox pixel matrix

        :param
            pixel (int matrix)             - rgb color values
        :return
            convertedPixels (float matrix) - hsv color values (faster than numpy)
        """

        width, height = self.cfg.width, self.cfg.height
        # faster than numpy
        self.covertedPixels = [[[0 for x in range(3)] for y in range(height)] for z in range(width)]

        for w in range(width):
            for h in range(height):
                # get pixel
                pixel = self.pixels[w, h]

                # convert to 0-1 interval
                pixel = image_handler.rgb2rgb(pixel)

                # covert to hsv
                self.covertedPixels[w][h] = colorsys.rgb_to_hsv(pixel[0], pixel[1], pixel[2])

    def import_satellite_image(self, imageFile):
        """
        importing saved map image for sensor area

        :param
            imageFile - saved map image

        :return:
            grids with their color information
        """
        self.pixels = imageFile.load()

        # self.convert_color_space()
        for grid in self.grids:
            self.set_grid_color(grid)

    # GRID FUNCTIONS
    def set_grid_color(self, grid):
        """
        set grid's color information (color averages and their standard deviation values)

        scan the grid from left to right and from top to bottom and find averages and std dev for each pixel's colors
        """

        c1, c2, c3 = [], [], []
        width, height = self.cfg.width, self.cfg.height

        # scan all grid area
        for coor in self.cfg.gridCoordinates:
            x = coor[0] + grid.xPos
            y = coor[1] + grid.yPos
            # coordinate should in the area
            if (0 <= x < width) and (0 <= y < height):
                pixel = self.pixels[x, y]

                c1 += [pixel[0]]
                c2 += [pixel[1]]
                c3 += [pixel[2]]

        if c1 and c2 and c3:
            grid.colorAvg, grid.colorStdDev = self.calc_avg_std([c1, c2, c3])

    def initialize_grids(self):
        """
        finding grids' locations and size ratios

        :return
            grids with their locations, and their size ratios
        """

        self.grids = []
        radius, edge = self.cfg.radius, self.cfg.gridEdge
        width, height = self.cfg.width, self.cfg.height
        columnCnt, rowCnt = self.cfg.columnCnt, self.cfg.rowCnt

        for r in range(rowCnt):
            for c in range(columnCnt):
                gridId = columnCnt * r + c

                xPos = ((gridId % columnCnt) * edge) + radius
                yPos = (r * edge) + radius

                xSize = edge if (xPos + radius) <= width else (width - xPos) + radius
                ySize = edge if (yPos + radius) <= height else (height - yPos) + radius

                sizeRatio = 1.0 if (xSize == edge) and (ySize == edge) else (xSize * ySize) / (edge ** 2.0)

                grid = Grid(gridId, xPos, yPos, sizeRatio)
                self.grids.append(grid)

    # SENSOR FUNCTIONS
    def find_connected_sensors(self, xPos, yPos, sensors):
        """
        finding connected sensors to find which sensors affected by current sensor

        :param
            xPos (int)            - x coordinate of sensor
            yPos (int)            - y coordinate of sensor
            sensors (Sensor list) - all sensors list
        """

        edgeSqr = self.cfg.gridEdge ** 2
        connectedList = []

        for sensor in sensors:
            dist = (xPos - sensor.xPos) ** 2 + (yPos - sensor.yPos) ** 2

            if dist <= edgeSqr:
                connectedList.append(sensor)

        return connectedList

    def get_intersection_sensors(self):
        """
        getting intersection point sensors (vertices of the grids)
        """

        intersectionSensors = []
        cnt = len(self.grids)
        edge = self.cfg.gridEdge
        width, height = self.cfg.width, self.cfg.height

        # from (0,0) to (width, height) all grid edge distances are intersection point
        for w in range(0, width + 1, edge):
            for h in range(0, height + 1, edge):
                sensor = Sensor(cnt, w, h)
                sensor.priority, c = self.calc_priority(sensor.xPos, sensor.yPos)

                intersectionSensors.append(sensor)
                cnt += 1

        return intersectionSensors

    # SENSOR DEPLOYMENT FUNCTIONS
    def cover(self, xPos, yPos, sensorId):
        """
        marking coverage matrix with sensor id if it is:
            - coordinate is not covered or
            - covered by another sensor which its id is bigger than current sensor id

        :param
            xPos (int)     - x coordinate of sensor
            yPos (int)     - y coordinate of sensor
            sensorId (int) - sensorId of current sensor

        :return
            covered coverageMatrix with sensorId
        """

        width, height = self.cfg.width, self.cfg.height
        cM = self.cfg.coverageMatrix

        for coor in self.cfg.sensorCoordinates:
            x = coor[0] + xPos
            y = coor[1] + yPos

            if (0 <= x < width) and (0 <= y < height):
                if cM[x][y] == -1 or sensorId <= cM[x][y]:
                    cM[x][y] = sensorId

    def uncover(self, xPos, yPos, sensorId):
        """
        unmarking coverage matrix coordinates which are covered by current sensor

        :param
            xPos (int)     - x coordinate of sensor
            yPos (int)     - y coordinate of sensor
            sensorId (int) - sensorId of current sensor

        :return
            uncovered coverageMatrix
        """

        width, height = self.cfg.width, self.cfg.height
        cM = self.cfg.coverageMatrix

        for coor in self.cfg.sensorCoordinates:
            x = coor[0] + xPos
            y = coor[1] + yPos

            if (0 <= x < width) and (0 <= y < height):
                if sensorId == cM[x][y]:
                    cM[x][y] = -1

    def calc_priority(self, xPos, yPos):
        """
        finding sensor's priority value and cluster number

        :param
            xPos (int)     - x coordinate of sensor
            yPos (int)     - y coordinate of sensor
            sensorId (int) - sensorId of current sensor

        :return:
            priority (float)          - priority value for sensor (clusterPriority * sizeRatio)
            nearestClusterIndex (int) - cluster number for sensor
        """

        coveredCnt = 0
        # c1, c2, c3 = [], [], []
        width, height = self.cfg.width, self.cfg.height
        cM = self.cfg.coverageMatrix

        rsum = 0
        bsum = 0
        gsum = 0
        rsumSq = 0
        bsumSq = 0
        gsumSq = 0

        for coor in self.cfg.sensorCoordinates:
            x = coor[0] + xPos
            y = coor[1] + yPos

            if (0 <= x < width) and (0 <= y < height):
                if cM[x][y] == -1:
                    pixel = self.pixels[x, y]

                    # c1 += [pixel[0]]
                    r = pixel[0]
                    rsum += r
                    rsumSq += r*r
                    # c2 += [pixel[1]]
                    g = pixel[1]
                    gsum += g
                    gsumSq += g*g
                    # c3 += [pixel[2]]
                    b = pixel[2]
                    bsum += b
                    bsumSq += b*b

                    coveredCnt += 1

        if coveredCnt > 1:
            sizeRatio = float(coveredCnt) / self.cfg.gridCoorCnt
            colorAvg = [rsum/coveredCnt, gsum/coveredCnt, bsum/coveredCnt]
            colorStdDev = [math.sqrt((rsumSq-(rsum*rsum)/coveredCnt)/(coveredCnt-1)),
                           math.sqrt((gsumSq-(gsum*gsum)/coveredCnt)/(coveredCnt-1)),
                           math.sqrt((bsumSq-(bsum*bsum)/coveredCnt)/(coveredCnt-1))
                           ]
            return self.find_cluster_and_priority(colorAvg, colorStdDev, sizeRatio)
        else:
            return 0.0, -1

    def cover_and_priority(self, xPos, yPos, sensorId):
        """
        marking coverage matrix with sensor id if it is:
            - coordinate is not covered or
            - covered by another sensor which its id is bigger than current sensor id

        and

        finding sensor's priority value and cluster number

        :param
            xPos (int)     - x coordinate of sensor
            yPos (int)     - y coordinate of sensor
            sensorId (int) - sensorId of current sensor

        :return:
            priority (float)          - priority value for sensor (clusterPriority * sizeRatio)
            nearestClusterIndex (int) - cluster number for sensor

            covered coverageMatrix with sensorId
        """

        coveredCnt = 0
        # c1, c2, c3 = [], [], []

        width, height = self.cfg.width, self.cfg.height
        cM = self.cfg.coverageMatrix

        rsum = 0
        bsum = 0
        gsum = 0
        rsumSq = 0
        bsumSq = 0
        gsumSq = 0

        for coor in self.cfg.sensorCoordinates:
            x = coor[0] + xPos
            y = coor[1] + yPos

            if (0 <= x < width) and (0 <= y < height):
                if cM[x][y] == -1 or sensorId <= cM[x][y]:
                    pixel = self.pixels[x, y]

                    # c1 += [pixel[0]]
                    r = pixel[0]
                    rsum += r
                    rsumSq += r*r
                    # c2 += [pixel[1]]
                    g = pixel[1]
                    gsum += g
                    gsumSq += g*g
                    # c3 += [pixel[2]]
                    b = pixel[2]
                    bsum += b
                    bsumSq += b*b
                    coveredCnt += 1
                    cM[x][y] = sensorId

        if coveredCnt > 1:
            colorAvg = [rsum/coveredCnt, gsum/coveredCnt, bsum/coveredCnt]
            colorStdDev = [math.sqrt((rsumSq-(rsum*rsum)/coveredCnt)/(coveredCnt-1)),
                           math.sqrt((gsumSq-(gsum*gsum)/coveredCnt)/(coveredCnt-1)),
                           math.sqrt((bsumSq-(bsum*bsum)/coveredCnt)/(coveredCnt-1))
                           ]
            sizeRatio = float(coveredCnt) / self.cfg.gridCoorCnt

            return self.find_cluster_and_priority(colorAvg, colorStdDev, sizeRatio)
        else:
            return 0.0, -1

    def clear_deployment(self):
        """
        removing sensors from sensor area
        """

        self.cfg.clear_coverage()
        self.sensors = []

    def pq_deployment(self):
        """
        priority queue deployment

        priority queue will create with fake sensors' priority values and always will be updated
        deploy sensors which will use location information of fake sensors which are in the priority queue

        if sensors are more than fake sensors (same number of grids) call to remaining deployment

        :param
            fakeSensors - assume that there are some sensors center of grids (original and from intersection points)

        :return
            deployed sensors in sensor area
        """

        print "\n-> Priority Queue Deployment"

        self.clear_deployment()

        fakeSensors = []

        for grid in self.grids:
            sensor = Sensor(grid.gridId, grid.xPos, grid.yPos)
            sensor.priority, c = self.calc_priority(sensor.xPos, sensor.yPos)

            fakeSensors.append(sensor)

        intersectionSensors = self.get_intersection_sensors()

        fakeSensors += intersectionSensors

        fakeSensors = filter(lambda s: s.priority != 0, fakeSensors)
        fakeSensors = sorted(fakeSensors, key=lambda s: s.priority)

        sensorCnt = self.cfg.sensorCnt
        for i in range(sensorCnt):
            best = fakeSensors.pop()

            sensor = Sensor(i, best.xPos, best.yPos, best.priority)
            self.cover(sensor.xPos, sensor.yPos, sensor.sensorId)
            self.sensors.append(sensor)

            connectedSensors = self.find_connected_sensors(sensor.xPos, sensor.yPos, fakeSensors)
            for s in connectedSensors:
                s.priority, c = self.calc_priority(s.xPos, s.yPos)

            fakeSensors = filter(lambda s: s.priority != 0, fakeSensors)
            fakeSensors = sorted(fakeSensors, key=lambda s: s.priority)

            if not fakeSensors:
                start = i + 1
                totalSensor = sensorCnt - start

                self.remaining_deployment(start, totalSensor)
                break

            log_message = "Sensor" + " " + str(sensor.sensorId) + " " + \
                          str(sensor.xPos) + " " + str(sensor.yPos) + " " + str(sensor.priority)
            self.notify(log_message)

        result = sum([sensor.priority for sensor in self.sensors])

        log_message = "PQ:" + " " + str(result)
        self.notify(log_message)
        print "Priority: " + str(result),

        return result

    def remaining_deployment(self, start, totalSensor):
        """
        deploy remaining sensors to next to best sensors which have better priority if sensors are more than grids

        :param
            start (int) - next sensor id
            totalSensor (int) - number of sensor will be deployed

        :return:
            deployed remaining sensors in sensor area
        """

        sensors = sorted(self.sensors, key=lambda sensor: sensor.priority)

        halfRadius = self.cfg.radius / 2.0
        quarterRadius = self.cfg.radius / 4.0

        for i in range(totalSensor):
            best = sensors[i % len(sensors)]

            moveX = int(round(halfRadius + quarterRadius * random.uniform(-1.0, 1.0))) * random.choice([1, -1])
            moveY = int(round(halfRadius + quarterRadius * random.uniform(-1.0, 1.0))) * random.choice([1, -1])

            sensor = Sensor(start + i, best.xPos + moveX, best.yPos + moveY)
            sensor.priority, c = self.cover_and_priority(sensor.xPos, sensor.yPos, sensor.sensorId)

            self.sensors.append(sensor)

            log_message = "Sensor" + " " + str(sensor.sensorId) + " " + \
                          str(sensor.xPos) + " " + str(sensor.yPos) + " " + str(sensor.priority)
            self.notify(log_message)

    def random_deployment(self):
        print "\n-> Random Deployment"

        self.clear_deployment()

        grids = filter(lambda g: g.priority != 0, self.grids)
        sensorCnt = self.cfg.sensorCnt
        width, height = self.cfg.width, self.cfg.height

        for i in range(sensorCnt):
            grid = random.choice(grids)
            grids.remove(grid)

            sensor = Sensor(i, grid.xPos, grid.yPos)
            sensor.priority, c = self.calc_priority(sensor.xPos, sensor.yPos)

            if sensor.priority != 0:
                self.cover(sensor.xPos, sensor.yPos, sensor.sensorId)
                self.sensors.append(sensor)

                log_message = "Sensor" + " " + str(sensor.sensorId) + " " + \
                              str(sensor.xPos) + " " + str(sensor.yPos) + " " + str(sensor.priority)
                self.notify(log_message)

            if not grids:
                start = i + 1
                totalSensor = sensorCnt - start

                for j in range(totalSensor):
                    xPos = random.randint(0, width)
                    yPos = random.randint(0, height)

                    sensor = Sensor(start + j, xPos, yPos)
                    sensor.priority, c = self.calc_priority(sensor.xPos, sensor.yPos)

                    log_message = "Sensor" + " " + str(sensor.sensorId) + " " + \
                                  str(sensor.xPos) + " " + str(sensor.yPos) + " " + str(sensor.priority)

                    if sensor.priority != 0:
                        self.cover(sensor.xPos, sensor.yPos, sensor.sensorId)
                        self.sensors.append(sensor)
                    else:
                        j -= 1

                    self.notify(log_message)
                break

        result = sum([sensor.priority for sensor in self.sensors])

        self.notify(result)
        print "Priority: " + str(result),

        return result

    # OPTIMIZATION FUNCTIONS
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

    def genetic_algorithms(self):
        print "\n-> Genetic Algorithm Deployment"

        self.clear_deployment()

        fakeSensors = []

        for grid in self.grids:
            sensor = Sensor(grid.gridId, grid.xPos, grid.yPos)
            sensor.priority, c = self.calc_priority(sensor.xPos, sensor.yPos)

            fakeSensors.append(sensor)

        intersectionSensors = self.get_intersection_sensors()

        fakeSensors += intersectionSensors

        # fakeSensors = filter(lambda s: s.priority != 0, fakeSensors)
        # fakeSensors = sorted(fakeSensors, key=lambda s: s.priority)

        sensorCnt = self.cfg.sensorCnt


        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        # creator.create("Individual", array.array, fitness=creator.FitnessMax)
        creator.create("Individual", list, fitness=creator.FitnessMax)

        toolbox = base.Toolbox()

        # Attribute generator
        toolbox.register("indices", random.sample, range(len(fakeSensors)), sensorCnt)

        # Structure initializers
        toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        def evalSD(individual):
            sensors = []

            for i, j in enumerate(individual):
                sensor = Sensor(i, fakeSensors[j].xPos, fakeSensors[j].yPos)
                sensor.priority, c = self.cover_and_priority(sensor.xPos, sensor.yPos, sensor.sensorId)

                # connectedSensors = self.find_connected_sensors(sensor.xPos, sensor.yPos, sensors)
                # for s in connectedSensors:
                #   s.priority, c = self.calc_priority(s.xPos, s.yPos)

                sensors.append(sensor)

            totalPriority = sum([sensor.priority for sensor in sensors])
            # print individual
            # print totalPriority

            self.cfg.clear_coverage()
            return totalPriority,

        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.05)
        toolbox.register("select", tools.selTournament, tournsize=3)
        toolbox.register("evaluate", evalSD)

        pop = toolbox.population(n=sensorCnt)

        hof = tools.HallOfFame(1)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", numpy.mean)
        stats.register("std", numpy.std)
        stats.register("min", numpy.min)
        stats.register("max", numpy.max)

        algorithms.eaSimple(pop, toolbox, 0.7, 0.2, 40, stats=stats,
                            halloffame=hof)
        # return pop, stats, hof

        print hof[0]
        for i, best in enumerate(hof[0]):
            sensor = Sensor(i, fakeSensors[best].xPos, fakeSensors[best].yPos)
            sensor.priority, c = self.cover_and_priority(sensor.xPos, sensor.yPos, sensor.sensorId)
            self.sensors.append(sensor)

            # connectedSensors = self.find_connected_sensors(sensor.xPos, sensor.yPos, fakeSensors)
            # for s in connectedSensors:
            #     s.priority, c = self.calc_priority(s.xPos, s.yPos)


            log_message = "Sensor" + " " + str(sensor.sensorId) + " " + \
                          str(sensor.xPos) + " " + str(sensor.yPos) + " " + str(sensor.priority)
            self.notify(log_message)


        result = sum([sensor.priority for sensor in self.sensors])

        log_message = "PQ:" + " " + str(result)
        self.notify(log_message)
        print "Priority: " + str(result),

        return result