import Pycluster
import numpy
from random import sample
from scipy.spatial.distance import euclidean

from cluster import Cluster


class SelfKMeans(Cluster):
    """
    k-means clustering algorithm implementation by us
    """

    def cost(self, data, clusters, memberships):
        squareSum = 0

        for i, datum in enumerate(data):
            squareSum += (euclidean(datum, clusters[memberships[i]]) ** 2)

        return (1 / data.shape[0]) * squareSum

    def cluster(self, data, clusterCnt, iteration=1000):
        """
        K-Means algorithm
        """

        # select the clusters randomly from data
        dataCount = data.shape[0]
        clusters = numpy.array(sample(data, clusterCnt))

        # assign random memberships to the data
        memberships = numpy.zeros(dataCount)

        # flags for the stop criteria
        changed = False
        currentIter = 0
        previousCost = 1e308

        # k-means loop starting
        while True:
            # reset new cluster variables
            newClusters = numpy.zeros((clusterCnt, data.shape[1]))
            newClusterSize = numpy.zeros(clusterCnt)

            # Cluster Assignment Step
            # assign each data to the nearest cluster
            for i, datum in enumerate(data):
                dMin = float('Inf')

                # find the smallest distance cluster center
                for j, cluster in enumerate(clusters):
                    distance = euclidean(datum, cluster)

                    if distance < dMin:
                        dMin = distance
                        n = j

                # assign closest cluster to the datum
                if memberships[i] != n:
                    memberships[i] = n
                    changed = True

                # store the sum of the all data belonging to the same cluster
                newClusters[memberships[i]] = newClusters[memberships[i]] + datum
                # store the data count of cluster
                newClusterSize[memberships[i]] += 1

            # Update Step
            # calculate new cluster centers using data cluster information
            for j in range(clusterCnt):
                if newClusterSize[j] > 0:
                    clusters[j] = newClusters[j] / newClusterSize[j]

            # Cost Calculation
            cost = self.cost(data, clusters, memberships)

            if previousCost == cost:
                break
            else:
                previousCost = cost

            currentIter += 1

            # check for stop criteria
            if currentIter > iteration or changed is False:
                break

        # data cluster memberships and cluster centers are returned
        print "iteration:", currentIter
        self.clusterCenters = clusters

        return memberships

    def find_cluster_centers(self, data, clusterCnt, rlabels):
        """
        finding cluster centers
        """

        data = numpy.array(data)
        centerMeans = numpy.zeros((clusterCnt, data.shape[1]))

        # find means
        for i in range(clusterCnt):
            a = numpy.where(rlabels == i)
            b = numpy.sum(data[a[0]], 0)

            centerMeans[i] = b / len(a[0])

        return centerMeans

    def test_pycluster(self, data, clusterCnt):
        """
        finding clusters of data
        """

        rlabels, error, nfound = Pycluster.kcluster(data, clusterCnt)

        self.clusterCenters = self.find_cluster_centers(data, clusterCnt, rlabels)

        # error because data is not integer
        # self.clusterCenters = numpy.vstack([data[rlabels == i].mean(0) for i in range(rlabels.max() + 1)])

        # returning cluster numbers for inputs
        return rlabels

if __name__ == "__main__":
    # testing
    ae = SelfKMeans()
    sampleData = numpy.array(
        [[0, 1, 2, 3, 4, 5],
         [1, 2, 3, 4, 5, 0],
         [2, 3, 4, 5, 0, 1],
         [3, 4, 5, 0, 1, 2]])

    print "cluster:", ae.cluster(sampleData, 2)