import numpy as np
from itertools import permutations

tlist = [(np.random.randint(low=0, high=10), np.random.randint(low=0, high=10)) for i in range(5)]
constraint_first_number = np.random.randint(low=5, high=20)
print(tlist, constraint_first_number)

for i in range(len(tlist)):
    for j in permutations(tlist, i + 1):
        if constraint_first_number > sum([x[0] for x in j]):
            print(j)
