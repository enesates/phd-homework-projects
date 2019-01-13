"""
Because of problems in scipy clustering we are using pycluster
http://bonsai.hgc.jp/~mdehoon/software/cluster/software.htm#pycluster

Required libraries: scipy, numpy, matplotlib, pylab
For FCM: bitarray

http://stackoverflow.com/questions/1545606/python-k-means-algorithm
"""

import Pycluster
import peach
import numpy

from cluster import Cluster


class KMeans(Cluster):
    """
    k-means clustering algorithm implementation using pycluster
    """

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

    def pycluster_kmeans(self, data, clusterCnt):
        """
        k-means implementation using PyCluster
        """
        rlabels, error, nfound = Pycluster.kcluster(data, clusterCnt)
        self.clusterCenters = self.find_cluster_centers(data, clusterCnt, rlabels)

        return rlabels

    def peach_kmeans(self, data, clusterCnt):
        """
        k-means implementation using Peach
        """
        km = peach.KMeans(data, clusterCnt)
        self.clusterCenters = km()

        rlabels = km.classify(data, self.clusterCenters)

        return rlabels

    def cluster(self, data, clusterCnt):
        """
        finding cluster of data
        """

        rlabels = self.pycluster_kmeans(data, clusterCnt)

        return rlabels


if __name__ == "__main__":
    # testing
    ae = KMeans()
    sampleData = numpy.array(
        [[0, 1, 2, 3, 4, 5],
         [1, 2, 3, 4, 5, 0],
         [2, 3, 4, 5, 0, 1],
         [3, 4, 5, 0, 1, 2]])

    print "cluster:", ae.pycluster_kmeans(sampleData, 2)
    print "cluster:", ae.peach_kmeans(sampleData, 2)