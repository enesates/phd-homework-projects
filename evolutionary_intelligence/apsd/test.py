fo = open("test.txt", "r")

if fo.readline().split()[1] == "Random":
    lines = [float(x.split()[1]) for x in fo if "Priority" in x]
else:
    lines = [x.split()[1] for x in fo if "Priority" in x]
    lines = [float(x) for i, x in enumerate(lines) if i % 3 == 1]

print lines, len(lines)
print sum(lines)/len(lines)

# izmir_cluster_estimation = [
#     [2, 2, 2, 2, 2, 2, 2, 1, 1, 0],
#     [2, 2, 2, 2, 2, 2, 0, 0, 0, 0],
#     [2, 2, 2, 2, 2, 1, 0, 0, 0, 0],
#     [2, 2, 2, 2, 1, 0, 0, 0, 0, 0],
#     [2, 2, 2, 1, 1, 0, 0, 0, 0, 0],
#     [1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
#     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# ]