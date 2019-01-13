from collections import defaultdict

class Graph():
    def __init__(self):
        self.nodes = []
        self.edges = defaultdict(list)
        self.distances = defaultdict(int)

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, first_node, last_node, distance):
        self.edges[first_node].append(last_node)
        self.edges[last_node].append(first_node)
        self.distances[(first_node, last_node)] = distance
        self.distances[(last_node, first_node)] = distance

def dijkstra(graph, source, target):
    current = source
    neighbour = graph.edges[current]
    visitMe = [source] + neighbour
    visited = []

    path = defaultdict(list)

    while visitMe:
        print '\nCurrent:', current
        print 'Neighbours:', neighbour

        visit = {}
        for q in neighbour:
            dist = graph.distances[(source, current)] + graph.distances[(current, q)]
            if graph.distances[(source, q)] and dist >= graph.distances[(source, q)]:
                visit[(source, q)] = graph.distances[(source, q)]
            else:
                visit[(source, q)] = dist
                graph.distances[(source, q)] = dist
                path[(source, q)] = path[(source, last)] + [current]

        best = min(visit, key=visit.get)
        visitMe.remove(current)
        visited.append(current)

        print 'Distances:', visit
        print 'Best:', best
        print 'Path:', path[best]
        print 'Visit Me:', visitMe

        if target in visitMe:
            visitMe.remove(target)
        if best:
            if best[1] == target:
                if not visitMe:
                    break
                current = visitMe[0]
            else:
                current = best[1]

        last = current
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

    print '\nResult'
    print '-------'
    print 'Path:', [source] + path[(source, target)] + [target]
    print 'Distance: ',  visit[(source, target)]


if __name__ == '__main__':
    g = Graph()

    with open('romania_cities.txt') as f:
        for city in f.readlines():
            g.add_node(city.strip())

    with open('romania_distances.txt') as f:
        lines = f.readlines()
        cities = list(g.nodes)

        for line, city in zip(lines, g.nodes):
            line = line.split()
            for dist, city2 in zip(line, g.nodes):
                dist = int(dist)
                if dist != 0:
                    g.add_edge(city, city2, dist)

    dijkstra(g, 'Arad', 'Bucharest')

    # g = Graph()
    # g.add_node(1)
    # g.add_node(2)
    # g.add_node(3)
    # g.add_node(4)
    # g.add_node(5)
    # g.add_node(6)

    # g.add_edge(1, 2, 7)
    # g.add_edge(1, 3, 11)
    # g.add_edge(1, 6, 14)
    # g.add_edge(2, 3, 10)
    # g.add_edge(2, 4, 5)
    # g.add_edge(3, 4, 11)
    # g.add_edge(3, 6, 20)
    # g.add_edge(4, 5, 16)
    # g.add_edge(5, 6, 9)

    # dijkstra(g, 1, 5)
