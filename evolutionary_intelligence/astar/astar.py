from collections import defaultdict

class Graph():
    def __init__(self):
        self.nodes = []
        self.edges = defaultdict(list)
        self.distances = defaultdict(int)
        self.s_distances = {}

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, first_node, last_node, distance):
        self.edges[first_node].append(last_node)
        self.edges[last_node].append(first_node)
        self.distances[(first_node, last_node)] = distance
        self.distances[(last_node, first_node)] = distance

def astar(graph, source, target):
    current = source
    neighbour = graph.edges[current]
    if target in neighbour:
        neighbour.remove(target)
    visitMe = [source] + neighbour
    visited = []

    path = defaultdict(list)

    visit = {}
    solution = {}

    while visitMe:
        print '\nCurrent:', current
        print 'Neighbours:', neighbour

        for q in neighbour:
            path[(source, q)] = path[(source, current)] + [current]
            graph.distances[(source, q)] = graph.distances[(source, current)] + graph.distances[(current, q)]

            if q == target:
                solution[graph.distances[(source, q)]] = path[(source, q)]
                dist = graph.distances[(source, q)]
            else:
                dist = graph.distances[(source, q)] + graph.s_distances[q]

            visit[(q, target)] = dist

        best = min(visit, key=visit.get)
        if best[0] == best[1]:
            break

        visitMe.remove(current)
        visited.append(current)

        print 'Distances:', visit
        print 'Best:', best
        print 'Path:', path[(source, best[0])]
        print 'Visit Me:', visitMe
        print 'Visited:', visited

        del visit[best]

        last = current
        current = best[0]
        neighbour = filter(lambda x: x not in visited, graph.edges[current])

        while (not neighbour and visitMe):
            visitMe.remove(current)
            visited.append(current)

            if visitMe:
                current = visitMe[0]
            else:
                break

            neighbour = filter(lambda x: x not in visited, graph.edges[current])

        for q in neighbour:
            if q not in visitMe:
                visitMe += neighbour

    sol = min(solution)
    print '\nResult'
    print '------'
    print 'Path:', solution[sol] + [target]
    print 'Distance:', sol


if __name__ == '__main__':
    g = Graph()
    cities = list(g.nodes)

    with open('romania_cities.txt') as f:
        for city in f.readlines():
            g.add_node(city.strip())

    with open('romania_straight_distances.txt') as f:
        lines = f.readlines()
        for dist, city in zip(lines, g.nodes):
            g.s_distances[city] = int(dist)

    with open('romania_distances.txt') as f:
        lines = f.readlines()
        cities = list(g.nodes)

        for line, city in zip(lines, g.nodes):
            line = line.split()
            for dist, city2 in zip(line, g.nodes):
                dist = int(dist)
                if dist != 0:
                    g.add_edge(city, city2, dist)

    astar(g, 'Arad', 'Bucharest')

    # g = Graph()
    # g.add_node('s')
    # g.add_node('a')
    # g.add_node('b')
    # g.add_node('c')
    # g.add_node('d')
    # g.add_node('e')
    # g.add_node('f')
    # g.add_node('t')
    #
    # g.add_edge('s', 'a', 1.5)
    # g.add_edge('s', 'd', 2)
    # g.add_edge('a', 'b', 2)
    # g.add_edge('b', 'c', 3)
    # g.add_edge('c', 't', 4)
    # g.add_edge('d', 'e', 3)
    # g.add_edge('e', 't', 3)
    # g.add_edge('e', 'f', 1)
    # g.add_edge('f', 't', 1)
    #
    # g.s_distances['a'] = 4
    # g.s_distances['b'] = 2
    # g.s_distances['c'] = 4
    # g.s_distances['d'] = 4.5
    # g.s_distances['e'] = 2
    # g.s_distances['f'] = 1

    # astar(g, 's', 't')
