"""
    feed forward multilayer perceptron from https://pythonhosted.org/neurolab/ex_newff.html
"""

import neurolab as nl
import neurolab.tool as nlTool
import numpy as np


class ANN:
    def __init__(self):
        self.inputs = []
        self.inputsNormalized = []

        self.targets = []
        self.targetsNormalized = []

    def estimateNEWFF(self, input, target):
        """
        training network
        """

        # prepare the data
        input = np.array(input)
        target = np.array(target)
        self.targets = target.reshape(len(target), 1)
        self.inputs = input.reshape(len(input), len(input[0]))

        # normalize the data
        self.norm_inp = nlTool.Norm(self.inputs)
        self.inputsNormalized = self.norm_inp(self.inputs)
        self.norm_tar = nlTool.Norm(self.targets)
        self.targetsNormalized = self.norm_tar(self.targets)

        # build the network
        self.net = nl.net.newff(nlTool.minmax(self.inputsNormalized), [40, 1])
        self.net.trainf = nl.train.train_rprop
        # train the network
        self.err = self.net.train(self.inputsNormalized, self.targetsNormalized, epochs=1000, show=100)

        print("\nTraining Error:" + str(self.err))

    def activate(self, netInput):
        """
        estimate class using network
        """

        netInput = np.array([netInput])
        inp = netInput.reshape(len(netInput), len(netInput[0]))

        inpNorm = self.norm_inp(inp)
        out = self.net.sim(inpNorm)
        outRenorm = self.norm_tar.renorm(out)[0][0]

        return outRenorm
