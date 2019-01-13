"""
    http://bonsai.hgc.jp/~mdehoon/software/cluster/software.htm#pycluster
    http://bonsai.hgc.jp/~mdehoon/software/cluster/Pycluster-1.52.tar.gz
    (in pycluster directory: python setup.py install)
"""

import Pycluster
import numpy


class KMeans:
    """
    k-means clustering algorithm implementation using pycluster
    """

    def __init__(self):
        """
        Constructor
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

    def cluster(self, data, clusterCnt):
        """
        finding cluster of data
        """

        rlabels, error, nfound = Pycluster.kcluster(data, clusterCnt)
        self.clusterCenters = self.find_cluster_centers(data, clusterCnt, rlabels)

        return rlabels

