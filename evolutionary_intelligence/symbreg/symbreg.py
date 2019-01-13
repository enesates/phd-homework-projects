# https://github.com/DEAP/deap/blob/master/examples/gp/symbreg.py

import operator
import math
import random
import numpy

from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

def protectedDiv(left, right):
    try:
        return left / right
    except ZeroDivisionError:
        return 1
def pow2(left):
    return pow(left,2)
def pow3(left):
    return pow(left,3)
def pow4(left):
    try:
        return pow(left,4)
    except OverflowError:
        return float('inf')
def pow5(left):
    try:
        return pow(left,5)
    except OverflowError:
        return float('inf')
pset = gp.PrimitiveSetTyped("MAIN", [float, float, float, float], float)
pset.addEphemeralConstant("rand101", lambda: random.randint(1, 5), int)
pset.addPrimitive(operator.add, [float, float], float)
pset.addPrimitive(operator.sub, [float, float], float)
pset.addPrimitive(operator.mul, [float, float], float)
pset.addPrimitive(protectedDiv, [float, float], float)
pset.addPrimitive(pow2, [float], float)
pset.addPrimitive(pow3, [float], float)
pset.addPrimitive(pow4, [float], float)
pset.addPrimitive(pow5, [float], float)

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

toolbox = base.Toolbox()
toolbox.register("expr", gp.genHalfAndHalf, pset=pset, min_=1, max_=5)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)

def evalSymbReg(individual, points, lines):
    func = toolbox.compile(expr=individual)
    try:
        sqerrors = ((func(*line) - float(line2))**2  for line, line2 in zip(points, lines))
        return math.fsum(sqerrors) / len(points),
    except OverflowError:
        return float('inf'),

with open('Q1_input.txt') as f:
    lines = f.readlines()
    l = []
    for ll in lines:
        k = []
        lll = ll.split()
        for kk in lll:
            k.append(float(kk))
        l.append(k)

with open('Q1_output.txt') as g:
    lines = g.readlines()

toolbox.register("evaluate", evalSymbReg, points=l, lines=lines)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)
toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))

def main():
    pop = toolbox.population(n=1000)
    hof = tools.HallOfFame(1)

    stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
    stats_size = tools.Statistics(len)
    mstats = tools.MultiStatistics(fitness=stats_fit, size=stats_size)
    mstats.register("avg", numpy.mean)
    mstats.register("std", numpy.std)
    mstats.register("min", numpy.min)
    mstats.register("max", numpy.max)

    pop, log = algorithms.eaSimple(pop, toolbox, 0.7, 0.05, 200, stats=mstats, halloffame=hof, verbose=True)

    print 'Best Individual: '
    for i in range(len(hof)):
        print hof[i]
    print hof[0].fitness

if __name__ == "__main__":
    main()
