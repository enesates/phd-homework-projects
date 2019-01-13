import math
import os


class Config:
    """
    global parameters

    :param
        width (int)  - image and drawing area width
        height (int) - image and drawing area height
        radius (int) - sensor radius length

        gridEdge (int)  - grid edge length
        gridArea (int)  - grid area
        rowCnt (int)    - row count in sensor area
        columnCnt (int) - column count in sensor area

        clusterCnt (int)           - cluster count
        clusterPriorities (float)  - priority value for each cluster
        clusteringMethod (Cluster) - method for clustering (kmeans, fuzzy c means)

        sensorCnt (int)           - total sensor count
        coverageMatrix (int)      - pixel coverage matrix which holds sensor ids of the corresponding (default: -1)

        sensorCoordinates (int list) - default coordinates for finding own pixels by each sensor
        sensorCoorCnt (int)          - number of sensor's coordinate
        gridCoordinates (int list)   - default coordinates for finding own pixels by each grid
        gridCoorCnt (int)            - number of grid's coordinate for using coverage ratio calculation

        gMapCrop (int)      - pixel size to cut google logo from satellite image
        appRootDir (string) - project root directory
        imgDir (string)     - default map image file directory
    """

    def __init__(self, width, height, radius, sensorCnt=75, clusterCnt=3, gMapCrop=50):
        self.width = width
        self.height = height
        self.radius = radius

        self.gridEdge = radius * 2
        self.gridArea = self.gridEdge ** 2
        self.rowCnt = 0
        self.columnCnt = 0

        self.clusterCnt = clusterCnt
        self.clusterPriorities = []
        self.clusteringMethod = None

        self.sensorCnt = sensorCnt
        self.coverageMatrix = [[-1] * height for i in range(width)]

        self.sensorCoordinates = []
        self.sensorCoorCnt = 0
        self.gridCoordinates = []
        self.gridCoorCnt = 0

        self.gMapCrop = gMapCrop
        self.appRootDir = os.path.dirname(os.path.abspath(__file__))
        self.imgDir = self.appRootDir + "/images/google_map.png"

        self.calc_row_column_count()
        self.find_sensor_coordinates()
        self.find_grid_coordinates()

    def __str__(self):
        return 'Global params: ',\
               'width =', self.width, 'height =', self.height, 'radius =', self.radius,\
               'row count =', self.rowCnt, 'column count =', self.columnCnt,\
               'cluster count =', self.clusterCnt, 'cluster priorities =', self.clusterPriorities,\
               "gMap crop =", self.gMapCrop

    def calc_row_column_count(self):
        """
        finding grid count in a row and column
        """

        self.rowCnt = int(math.ceil(float(self.height) / self.gridEdge))
        self.columnCnt = int(math.ceil(float(self.width) / self.gridEdge))

    def find_sensor_coordinates(self):
        """
        finding covered coordinates for the sensor which has default location (xPos = radius, yPos = radius)

        :param
            start (int)   - minimum x and y position value
            end (int)     - maximum x and y position value
            centerX (int) - default sensor's x position
            centerY (int) - default sensor's y position

        :return
            Scanning Coordinates list for another sensors' covered coordinates
        """

        start, end = self.radius * -1, self.radius
        centerX = centerY = 0
        self.sensorCoorCnt = 0

        for xPos in range(start, end):
            for yPos in range(start, end):
                dist = math.sqrt((xPos - centerX) ** 2 + (yPos - centerY) ** 2)

                if dist <= self.radius:
                    self.sensorCoordinates.append([xPos, yPos])
                    self.sensorCoorCnt += 1

    def find_grid_coordinates(self):
        """
        finding covered coordinates for the grid which has default location (xPos = radius, yPos = radius)

        :param
            start (int) - minimum x and y position value
            end (int)   - maximum x and y position value

        :return
            Scanning Coordinates list for another grids' covered coordinates
        """

        start, end = self.radius * -1, self.radius
        self.gridCoorCnt = 0

        for xPos in range(start, end):
            for yPos in range(start, end):
                self.gridCoordinates.append([xPos, yPos])
                self.gridCoorCnt += 1

    def clear_coverage(self):
        """
        cleaning sensor ids information in coverage matrix

        :return
            zeros matrix for coverage matrix
        """

        self.coverageMatrix = [[-1] * self.height for i in range(self.width)]
