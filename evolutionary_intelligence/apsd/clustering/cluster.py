from scipy.spatial.distance import euclidean


class Cluster():
    """
    this abstract class is used for clustering operations
    """

    def __init__(self):
        """
        Constructor
        """

    def cluster(self, data, clusterCnt):
        """
        finding clusters of data
        """

        raise NotImplementedError("Should have implemented this")

    def find_nearest_cluster(self, data):
        """
        finding cluster center of only 1 data point
        """

        minDistance = 0
        nearestClusterIndex = -1

        for i in range(self.clusterCenters.shape[0]):
            distance = euclidean(data, self.clusterCenters[i])

            if i == 0:
                minDistance = distance
                nearestClusterIndex = 0
            elif minDistance > distance:
                minDistance = distance
                nearestClusterIndex = i

        return nearestClusterIndex