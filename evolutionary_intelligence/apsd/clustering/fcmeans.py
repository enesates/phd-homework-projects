import peach
import numpy as numpy

from cluster import Cluster


class FCMeans(Cluster):
    """
    fuzzy c-means clustering algorithm implementation using peach
    """

    def random_membership(self, n):
        x = [numpy.random.random() for i in range(n)]
        k = 1.0 / sum(x)

        return numpy.array([v * k for v in x])

    def random_membership_matrix(self, data, clusterCnt):
        mu = numpy.array([])

        for i in range(len(data)):
            mu = numpy.append(mu, self.random_membership(clusterCnt))

        mu.shape = len(data), clusterCnt

        return mu

    def cluster(self, data, clusterCnt):
        """
        finding clusters of data
        """

        # finding membership values depends on the cluster count
        mu = self.random_membership_matrix(data, clusterCnt)

        fcm = peach.FuzzyCMeans(data, mu)
        fcm(emax=0)

        self.clusterCenters = fcm.c

        # result is equal to max membership value
        result = []

        for a in fcm.mu:
            clusterIndex = numpy.where(a == max(a))[0][0]
            result.append(clusterIndex)

        # TODO: return with membership values or just clusters?
        # return result, fcm.mu
        return result

if __name__ == "__main__":
    # testing
    ae = FCMeans()
    sampleData = numpy.array(
        [[0, 1, 2, 3, 4, 5],
         [1, 2, 3, 4, 5, 0],
         [2, 3, 4, 5, 0, 1],
         [3, 4, 5, 0, 1, 2]])

    print ae.cluster(sampleData, 2)

    # example 2 - Peach - Computational Intelligence for Python - Jose Alexandre Nalon
    # We create the example list (the training set) and the corresponding
    # membership values for each example. There are 15 two-dimensional examples,
    # and 15 pairs of membership values. This means that each example will be
    # classified in two classes, with the corresponding membership values. This
    # [ 0, 0 ] will be classified with membership values 0.7 in the first class
    # and means that the vector membership values 0.3 in the second class and
    # so on. Notice that, with this values, we expect the two centers, after the
    # clustering, to be located at [ 1., 1. ] and [ 6., 6. ].
    x = numpy.array([
        [0., 0.], [0., 1.], [0., 2.], [1., 0.], [1., 1.], [1., 2.],
        [2., 0.], [2., 1.], [2., 2.], [5., 5.], [5., 6.], [5., 7.],
        [6., 5.], [6., 6.], [6., 7.], [7., 5.], [7., 6.], [7., 7.]])

    mu = numpy.array([
        [0.7, 0.3], [0.7, 0.3], [0.7, 0.3], [0.7, 0.3], [0.7, 0.3],
        [0.7, 0.3], [0.7, 0.3], [0.7, 0.3], [0.7, 0.3], [0.3, 0.7],
        [0.3, 0.7], [0.3, 0.7], [0.3, 0.7], [0.3, 0.7], [0.3, 0.7],
        [0.3, 0.7], [0.3, 0.7], [0.3, 0.7]])

    # Notice that the starting values for the memberships could be randomly
    # choosen, at least for simple cases like this. You could try the lines
    # below to initialize the membership array:
    #
    # from numpy.random import random
    # mu = random((18, 1))
    # mu = hstack((mu, 1.-mu))

    # This parameter measures the smoothness of convergence
    m = 2.0

    # We create the algorithm. We must pass, in this order, the example set, the
    # corresponding membership values, and the parameter `m`. This parameter is
    # optional, though, and if not given, will default to 2.
    fcm = peach.FuzzyCMeans(x, mu, m)

    # The __call__ interface runs the algorithm till completion. It returns the
    # center of the classification. If we want to check the membership values for
    # the vectors, the .mu instance variable can be checked. Notice that we pass
    # the parameter emax = 0 to the algorithm. This is the maximum error accepted.
    # In general, fuzzy c-means will converge very fastly and with little error. A
    # imax parameter -- the maximum number of iterations, can also be given. If it
    # isn't given, 20 iterations will be assumed.
    print "After 20 iterations, the algorithm converged to the centers:"
    print fcm(emax=0)
    print
    print "The membership values for the examples are given below:"
    print fcm.mu
    print
