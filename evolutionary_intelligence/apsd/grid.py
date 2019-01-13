class Grid():
    """
    grid object

    :param
        gridId (int)             - id (starts at 0)

        xPos (int)               - location's x position
        yPos (int)               - location's y position

        priority (float)         - priority value which is coming from clusters
        sizeRatio (float)        - ratio of grid's area (if it is not complete)

        clusterNum (int)         - grid's cluster number

        colorAvg (float list)    - color averages of pixels which is covered by grid
        colorStdDev (float list) - standard deviations of color values
    """

    def __init__(self, gridId, xPos, yPos, sizeRatio, priority=0.0):
        self.gridId = gridId

        self.xPos = xPos
        self.yPos = yPos

        self.priority = priority
        self.sizeRatio = sizeRatio

        self.clusterNum = -1

        self.colorAvg = [None] * 3
        self.colorStdDev = [None] * 3

    def __str__(self):
        return 'Grid: ',\
               'id =', self.gridId, 'priority =', self.priority,\
               'xPos =', self.xPos, 'yPos =', self.yPos,\
               'size ratio =', self.sizeRatio, 'cluster number =', self.clusterNum,\
               'color average =', self.colorAvg, 'color std dev =', self.colorStdDev