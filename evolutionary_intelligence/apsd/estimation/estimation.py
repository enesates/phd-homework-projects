import math
import numpy

from pybrain.tools.shortcuts import buildNetwork
from pybrain.supervised.trainers import BackpropTrainer
from pybrain.datasets.supervised import SupervisedDataSet
import neurolab


class Estimation():
    """
    this class is used for estimation
    (http://www.pybrain.org/docs/index.html)
    """

    def __init__(self):
        """
        Constructor
        """

    def normalization(self, x):
        return x / 255.0

    def train_data(self, data, neuronCnt):
        """
        to build and train the network

        data creation example:
            data = SupervisedDataSet(6,1)
            data.addSample((RA,GA,BA,RS,GS,BS),(T))

        :return
            trained data
        """

        # set training data
        self.trainingData = data

        # build the network
        self.net = buildNetwork(6, neuronCnt, 1)

        # train the network using back-propagation using training data
        self.trainer = BackpropTrainer(self.net, self.trainingData)

        # train for 1000 epoch
        for i in range(0, 1000):
            error = self.trainer.train()

        print "Training Error:", str(error)

    def activate(self, netInput):
        """
        activate network with netInput

        :return
            estimated priority
        """

        output = self.net.activate(netInput)[0]
        print output

        if output < 0.05:
            return 0
        else:
            return 1

    def estimate_ann(self, grids, neuronCnt):
        """
        estimation with artificial neural networks

        :param
            grids - grid list which will be used for training and estimating
        :return
            estimated priority values for grids
        """

        # prepare the data
        data = SupervisedDataSet(6, 1)
        
        for g in grids:
            if g.clusterNum >= 0:
                inp = (g.colorAvg[0], g.colorAvg[1], g.colorAvg[2],
                       g.colorStdDev[0], g.colorStdDev[1], g.colorStdDev[2])
                target = g.clusterNum

                data.addSample(inp, target)

        # train the ann
        self.train_data(data, neuronCnt)

        # now activate for other grid cells and find their priorities
        for g in grids:
            if g.clusterNum == -1:
                netInput = (g.colorAvg[0], g.colorAvg[1], g.colorAvg[2],
                            g.colorStdDev[0], g.colorStdDev[1], g.colorStdDev[2])

                g.clusterNum = self.activate(netInput)

    def pnn(self, dimension, sigma, testExample, trainingDatum):
        """
        Source : http://homepages.gold.ac.uk/nikolaev/311pnn.htm
        Additional resource:
        http://urrg.eng.usm.my/index.php?option=com_content&view=article&id=172:probabilistic-neural-network-pnn-algorithm&catid=31:articles&Itemid=70
        """

        c = 2
        classify = -1
        largest = 0
        sumK = [0, 0]

        # The OUTPUT layer which computes the pdf for each class C
        for k in range(c):
            trainingDatum = trainingDatum[k]  # 0 and 1 clusters
            nk = len(trainingDatum)  # number of training data in the cluster

            # the SUMMATION layer which accumulates the pdf for each example from the particular class k
            for i in range(nk):
                product = 0

                # the PATTERN layer that multiplies the test example by the weights
                for j in range(dimension):
                    product += testExample[j] * trainingDatum[i][j]

                product = (product - 1) / (sigma * sigma)
                product = math.exp(product)
                sumK[k] += product

            sumK[k] /= nk

        for k in range(c):
            if sumK[k] > largest:
                largest = sumK[k]
                classify = k

        return classify

    def estimate_pnn(self, grids):
        """
        estimation with probabilistic neural networks
        """

        # prepare the data
        cluster0 = []
        cluster1 = []
        clusters = []

        for g in grids:
            if g.clusterNum >= 0:
                data = [g.colorAvg[0], g.colorAvg[1], g.colorAvg[2],
                        g.colorStdDev[0], g.colorStdDev[1], g.colorStdDev[2]]
                data = map(self.normalization, data)

                if g.clusterNum == 0:
                    cluster0.append(data)
                else:
                    cluster1.append(data)

        clusters.append(cluster0)
        clusters.append(cluster1)

        for g in grids:
            if g.clusterNum == -1:
                data = [g.colorAvg[0], g.colorAvg[1], g.colorAvg[2],
                        g.colorStdDev[0], g.colorStdDev[1], g.colorStdDev[2]]
                data = map(self.normalization, data)

                g.clusterNum = self.pnn(len(data), 1, data, clusters)

    def estimate_newff(self, grids):
        """
        Using neurolab, for MATLAB similar API syntax and more NN techniques
        http://code.google.com/p/neurolab/
        """

        # prepare the data
        inp = []
        target = []

        for g in grids:
            if g.clusterNum >= 0:
                inp.append([g.colorAvg[0], g.colorAvg[1], g.colorAvg[2],
                            g.colorStdDev[0], g.colorStdDev[1], g.colorStdDev[2]])
                target.append(g.clusterNum)

        c1, c2, c3, std1, std2, std3 = [i[0] for i in inp], [i[1] for i in inp], [i[2] for i in inp],\
                                       [i[3] for i in inp], [i[4] for i in inp], [i[5] for i in inp],

        inp = numpy.array(inp)
        target = numpy.array(target)
        inp = inp.reshape(len(inp), 6)
        tar = target.reshape(len(target), 1)

        # build the network
        net = neurolab.net.newff([[min(c1), max(c1)], [min(c2), max(c2)], [min(c3), max(c3)],
                                 [min(std1), max(std1)], [min(std2), max(std2)], [min(std3), max(std3)]],
                                 [20, 1])
        # train the network
        err = net.train(inp, tar, epochs=1000, show=100)

        # now activate for other grid cells and find their priorities
        for g in grids:
            if g.clusterNum == -1:
                inp = [[g.colorAvg[0], g.colorAvg[1], g.colorAvg[2],
                        g.colorStdDev[0], g.colorStdDev[1], g.colorStdDev[2]]]

                inp = numpy.array(inp)
                inp = inp.reshape(len(inp), 6)
                out = net.sim(inp)

                g.clusterNum = 1 if out >= 0.5 else 0

    def estimate_lvq(self, grids):
        """
        Using neurolab, for MATLAB similar API syntax and more NN techniques
        http://code.google.com/p/neurolab/
        """

        # prepare the data
        inp = []
        target = []

        for g in grids:
            if g.clusterNum >= 0:
                inp.append([g.colorAvg[0], g.colorAvg[1], g.colorAvg[2],
                            g.colorStdDev[0], g.colorStdDev[1], g.colorStdDev[2]])
                target.append(g.clusterNum)

        inp = numpy.array(inp)
        target = numpy.array(target)
        inp = inp.reshape(len(inp), 6)
        tar = target.reshape(len(target), 1)

        # build the network
        net = neurolab.net.newlvq(neurolab.tool.minmax(inp), 10, [1])

        # train the network
        error = net.train(inp, tar, epochs=1000, goal=-1, show=100)

        # now activate for other grid cells and find their priorities
        for g in grids:
            if g.clusterNum == -1:
                inp = [[g.colorAvg[0], g.colorAvg[1], g.colorAvg[2],
                        g.colorStdDev[0], g.colorStdDev[1], g.colorStdDev[2]]]

                inp = numpy.array(inp)
                inp = inp.reshape(len(inp), 6)
                out = net.sim(inp)

                print inp[out[:, 0]]
                g.clusterNum = 1 if out >= 0.5 else 0


if __name__ == "__main__":
    # testing
    ae = Estimation()

    sampleData = SupervisedDataSet(6, 1)
    sampleData.addSample((0, 1, 2, 3, 4, 5), 3)
    sampleData.addSample((1, 2, 3, 4, 5, 0), 2)
    sampleData.addSample((2, 3, 4, 5, 0, 1), 5)
    sampleData.addSample((3, 4, 5, 0, 1, 2), 7)

    ae.train_data(sampleData, 20)

    print("Test Result:" + str(ae.activate([1, 2, 3, 4, 5, 0])))