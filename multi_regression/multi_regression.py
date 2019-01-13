import sys
import math
import time
import numpy as np
import matplotlib.pyplot as plt

featureMatrix = []
sureler = []
N = 0

def xfrange(start, stop, step):
    i = 0
    while start + i * step <= stop:
        yield start + i * step
        i += 1

def read_data(fileName):
    global N, featureMatrix, sureler

    featureMatrix = np.loadtxt(fileName)
    sureler = featureMatrix[:, [0]]
    featureMatrix = featureMatrix[:, 1:]
    N = len(featureMatrix)

# O(n^3)
def bf(lBound, uBound, interval):
    print "\nbrute force =>"
    globalMinRSS = float('inf')

    plt.axis([0, 100, 0, 5000])
    plt.ion()
    i = 0

    start = time.time()
    for w0 in xfrange(lBound, uBound, interval):
        minRSS = float('inf')
        for w1 in xfrange(lBound, uBound, interval):
            for w2 in xfrange(lBound, uBound, interval):
                for w3 in xfrange(lBound, uBound, interval):
                    for w4 in xfrange(lBound, uBound, interval):

                       RSS = 0
                       for (features, sure) in zip(featureMatrix, sureler):
                           # multiplication of w(i) and features
                           Hx = [a*b for a, b in zip(features, [w1, w2, w3, w4])]
                           y = w0 + sum(Hx)
                           RSS += math.pow(sure - y, 2)

                       if RSS < minRSS:
                           minRSS = RSS
                           minw0 = w0
                           minw1 = w1
                       else:
                           break

                    if minRSS < globalMinRSS:
                        globalMinRSS = minRSS
                        globalMinw0 = minw0
                        globalMinw1 = minw1

                    plt.scatter(i, globalMinRSS)

                    i += 1
                    plt.show()

                    print globalMinRSS

    finish = time.time()

    print "y =", globalMinw0, "+", globalMinw1, " x"
    print globalMinw1
    print "minRSS =", globalMinRSS
    print "time =", finish - start

    while True:
        plt.pause(0.5)

# O(n^3)
def cf():
    print "\nclosed form =>"
    global featureMatrix, sureler

    hTh = np.dot(featureMatrix.T, featureMatrix)
    hThInv = np.linalg.inv(hTh)
    hThInvhT = np.dot(hThInv, featureMatrix.T)
    w = np.dot(hThInvhT, sureler)

    print w

# O(m*n + k) => O(n)
def gd(eta, w0, w1, w2, w3, w4):
    print "\ngradient descent =>"
    global featureMatrix, sureler

    coefficients = [w0, w1, w2, w3, w4]
    lenCoef = len(coefficients)
    partial = lenCoef * [0]

    plt.axis([0, 100, 0, 5000])
    plt.ion()
    i = 0
    RSS = 1000

    while (RSS) > 0.01:
        for j in range(lenCoef):
            sumOf = 0
            for i in range(N):
                Hx = [a*b for a, b in zip(featureMatrix[i], coefficients[1:])]
                yi = w0 + sum(Hx)

                print i,j
                if j == 0:
                    sumOf += sureler[i] - yi
                else:
                    sumOf += featureMatrix[i][j-1] * (sureler[i] - yi)
            partial[j] = -2 * sumOf

            coefficients[j] -= (eta * partial[j])

        RSS = sum(a ** 2 for a in partial) ** 0.5
        print RSS

        plt.scatter(i, RSS)
        i += 1
        plt.show()
        plt.pause(0.5)

    while True:
        plt.pause(0.5)


if __name__ == '__main__':
    fileName = sys.argv[1]
    funcName = sys.argv[2]
    params = [float(i) for i in sys.argv[3:]]

    functions = {
        "bf" : bf,
        "cf" : cf,
        "gd" : gd
    }

    read_data(fileName)
    functions[funcName](*params)
