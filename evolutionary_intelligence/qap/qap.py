# -*-  coding: utf-8 -*-
# https://github.com/DEAP/deap/blob/master/examples/ga/onemax.py
# usage: python qap.py Tai12a.dat

import random
import time
import sys

from deap import base
from deap import creator
from deap import tools

# Tai or other data set
try:
    filename = sys.argv[1]
except:
    print("Please enter a file name")
    sys.exit()
# keep calculated fitnesses
calculated = {}

# read data from file
with open(filename) as f:
    lines = f.readlines()
    SIZE = int(lines[0])

    DISTANCES = [map(int, line.split()) for line in lines[2:SIZE+2]]
    FLOWS = [map(int, line.split()) for line in lines[SIZE+3:SIZE*2+3]]

L = SIZE
PC = 0.8
PM = 0.05
POPULATION_SIZE = 300
NGEN = 100
SELECTION = 'Tournament'
MUT_PB = 1.0
TOURN_SIZE = 9

factories = range(SIZE)

# define minimization
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

# define individual as an integer list
toolbox = base.Toolbox()
toolbox.register("attr_bool", random.sample, range(SIZE), SIZE)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.attr_bool)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

# fitness function
def evalQAP(individual):
    tupleInd = tuple(individual)
    total = calculated.get(tupleInd)

    if not total:
        total = 0
        for i in factories:
            for j in factories:
                total += DISTANCES[i][j] * FLOWS[individual[i]][individual[j]]

        calculated[tupleInd] = total

    return total,

# 2-opt local search algorithm
def twoOpt(ind):
    minVal = evalQAP(ind)

    # choose two bits randomly and swap them
    for i in range(SIZE*2):
        sample = random.sample(factories, 2)
        ind[sample[0]], ind[sample[1]] = ind[sample[1]], ind[sample[0]]

        newVal = evalQAP(ind)

	# keep new solution if it is better
        if newVal <= minVal:
            minVal = newVal
        else:
            ind[sample[0]], ind[sample[1]] = ind[sample[1]], ind[sample[0]]

    return ind


# operator registration
toolbox.register("evaluate", evalQAP)
toolbox.register("mate", tools.cxPartialyMatched)
toolbox.register("mutate", tools.mutShuffleIndexes, indpb=PM)
toolbox.register("select", tools.selTournament, tournsize=TOURN_SIZE)
toolbox.register("twoOpt", twoOpt)


def main():
    global calculated
    calculated = {}

    # create an initial population of POPULATION_SIZE individuals
    # (where each individual is a list of integers)
    pop = toolbox.population(n=POPULATION_SIZE)
    hof = tools.HallOfFame(1)

    print("- Start of evolution -")
    start = time.time()

    # evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    hof.update(pop)

    # begin the evolution
    for g in range(NGEN):
        print("-- Generation %i --" % (g+1))

        # select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        # apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            # cross two individuals with probability PC
            if random.random() < PC:
                toolbox.mate(child1, child2)

                # fitness values of the children  must be recalculated later
                del child1.fitness.values
                del child2.fitness.values

        for mutant in offspring:
            # mutate an individual with probability MUT_PB
            if random.random() < MUT_PB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

	    # local search using 2-opt
            toolbox.twoOpt(mutant)
            del mutant.fitness.values

        # evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        hof.update(pop)
        # the population is entirely replaced by the offspring
        pop[:] = offspring

	# best fitness in offspring and population during the evolution
        fits = [ind.fitness.values[0] for ind in pop]
        min_fit = min(fits)
        best_ind = [i+1 for i in hof[-1]]
        print("Min %s" % min_fit)
        print("Best individual is %s" % best_ind)
        print("Fitness: %s\n" % hof.keys[-1])

    end = time.time()
    run_time = end-start

    best_ind = [i+1 for i in hof[-1]]

    with open(str(SIZE)+'.txt', 'a') as the_file:
        the_file.write("Best individual is %s" % best_ind)
        the_file.write("\nFitness: %s" % hof.keys[-1])
        the_file.write("\nRun time: %s\n\n" % run_time)

    print("Best individual is %s" % best_ind)
    print("Fitness: %s" % hof.keys[-1])
    print("Run time: %s" % run_time)
    print("- End of evolution -\n\n")


if __name__ == "__main__":
    for i in range(10):
        main()
