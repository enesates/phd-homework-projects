# -*-  coding: utf-8 -*-

# https://github.com/DEAP/deap/blob/7b35c116b7ae4e151aea9577478f9053a8ee9278/examples/ga/onemax.py

import random
import time

from deap import base
from deap import creator
from deap import tools

L = 100
PC = 0.7
PM = 1.0 / L
POPULATION_SIZE = 100
NGEN = 1000
SELECTION = 'SUS'  # Roulette, Tournament, SUS
MUT_PB = 1.0
TOURN_SIZE = 2


creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()

# Attribute generator define 'attr_bool' to be an attribute ('gene') which
# corresponds to integers sampled uniformly from the range [0,1]
# (i.e. 0 or 1 with equal probability)
toolbox.register("attr_bool", random.randint, 0, 1)

# Structure initializers define 'individual' to be an individual
# consisting of L 'attr_bool' elements ('genes')
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, L)

# define the population to be a list of individuals
toolbox.register("population", tools.initRepeat, list, toolbox.individual)


# the goal ('fitness') function to be maximized
def evalOneMax(individual):
    match = 0

    for i in range(1, L-1):
        if individual[i] == 0:
            match += 1
    if individual[0] == 1:
        match += 1
    if individual[-1] == 1:
        match += 1

    return match,


# Operator registration
# ----------
# register the goal / fitness function
toolbox.register("evaluate", evalOneMax)

# register the crossover operator
toolbox.register("mate", tools.cxOnePoint)

# register a mutation operator with a probability to flip each attribute/gene of PM
toolbox.register("mutate", tools.mutFlipBit, indpb=PM)

# operator for selecting individuals for breeding the next generation
if SELECTION == 'Roulette':
    toolbox.register("select", tools.selRoulette)
elif SELECTION == 'SUS':
    toolbox.register("select", tools.selStochasticUniversalSampling)
elif SELECTION == 'Tournament':
    toolbox.register("select", tools.selTournament, tournsize=TOURN_SIZE)


# ----------
def main():
    # random.seed(64)

    # create an initial population of POPULATION_SIZE individuals
    # (where each individual is a list of integers)
    pop = toolbox.population(n=POPULATION_SIZE)

    print("- Start of evolution -")
    start = time.time()

    # Evaluate the entire population
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):
        ind.fitness.values = fit

    generation = []

    # Begin the evolution
    for g in range(NGEN):
        # print("-- Generation %i --" % g)

        # Select the next generation individuals
        offspring = toolbox.select(pop, len(pop))
        # Clone the selected individuals
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation on the offspring
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

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # The population is entirely replaced by the offspring
        pop[:] = offspring

        # Gather all the fitnesses in one list and print the stats
        fits = [ind.fitness.values[0] for ind in pop]

        length = len(pop)
        mean = sum(fits) / length
        sum2 = sum(x*x for x in fits)
        std = abs(sum2 / length - mean**2)**0.5
        max_fit = max(fits)
        min_fit = min(fits)

        # print("  Min %s" % min_fit)
        # print("  Max %s" % max_fit)
        # print("  Avg %s" % mean)
        # print("  Std %s" % std)

        generation.append([min_fit, max_fit, mean, std])

        if L == max_fit:
            break

    end = time.time()
    run_time = end-start

    best_ind = tools.selBest(pop, 1)[0]
    print("  Best individual is %s" % best_ind)
    print("  Fitness: %s" % best_ind.fitness.values[0])
    print("  Run time: %s" % run_time)
    print("- End of (successful) evolution -\n")

    return generation, run_time


def run_multiple_times(iter):
    gens = []
    runs = []
    for i in xrange(iter):
        gen, run_time = main()
        gens.append(gen)
        runs.append(run_time)

    len_runs = len(runs)
    mean_runs = sum(runs) / len_runs
    sum2_runs = sum(x*x for x in runs)
    std_runs = abs(sum2_runs / len_runs - mean_runs**2)**0.5

    avg_generations = sum(len(g) for g in gens) / float(len(gens))

    print("\nParams:")
    print("-------")
    print("  Bitstring: %s" % L)
    print("  Population size: %s" % POPULATION_SIZE)
    print("  Generation number: %s" % NGEN)
    print("  Crossover probability: %s" % PC)
    print("  Mutation probability: %s" % PM)
    print("  Parent selection: %s" % SELECTION)

    print("\nFirst run generations:")
    print("----------------------")
    print("  %s" % gens[0])

    print("\nAfter %s runs:" % iter)
    print("--------------")
    print("  mean of the time: %s sec." % mean_runs)
    print("  standard deviation of the time: %s sec." % std_runs)
    print("  average number of generations: %s" % avg_generations)


if __name__ == "__main__":
    run_multiple_times(10)



