# https://github.com/DEAP/deap/blob/master/examples/gp/multiplexer.py
import operator
import math
import random
import numpy
from deap import algorithms
from deap import base
from deap import creator
from deap import tools
from deap import gp

pset = gp.PrimitiveSet("MAIN", 17, 'IN')
pset.addPrimitive(operator.and_, 2)
pset.addPrimitive(operator.or_, 2)
pset.addPrimitive(operator.not_, 1)

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMax)
toolbox = base.Toolbox()
toolbox.register("expr", gp.genFull, pset=pset, min_=2, max_=4)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("compile", gp.compile, pset=pset)

def evalMultiplexer(individual, points, lines):
    func = toolbox.compile(expr=individual)

    return sum(func(*line) == int(line2) for line, line2 in zip(points, lines)),

with open('Q2_input.txt') as f:
    lines = f.readlines()
    l = []
    for i in lines:
        g = map(int, i.strip())
        l.append(g)

with open('Q2_output.txt') as g:
    lines = g.readlines()

toolbox.register("evaluate", evalMultiplexer, points=l, lines=lines)
toolbox.register("select", tools.selTournament, tournsize=7)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genGrow, min_=0, max_=2)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)

def main():
    pop = toolbox.population(n=40)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", numpy.mean)
    stats.register("std", numpy.std)
    stats.register("min", numpy.min)
    stats.register("max", numpy.max)

    algorithms.eaSimple(pop, toolbox, 0.8, 0.1, 40, stats=stats, halloffame=hof, verbose=True)

    print 'Best Individual: '
    for i in range(len(hof)):
        print hof[i]
    print hof[0].fitness

if __name__ == "__main__":
    main()
