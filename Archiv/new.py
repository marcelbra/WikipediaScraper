from collections import defaultdict

graph = {
     1: [2, 3],
     2: [1, 4, 5],
     3: [1, 6],
     4: [2, 7, 8],
     5: [2, 9],
     6: [3],
     7: [4, 10, 11],
     8: [4, 12, 13],
     9: [5],
    10: [7, 14],
    11: [7],
    12: [8],
    13: [8, 15, 16],
    14: [10],
    15: [13],
    16: [13],
}

graph = defaultdict(list, graph)


def listify(tuples):
    return [item for t in tuples for item in t]

def flattify(list_of_lists):
    """Makes the list flat and removes double occurences."""
    return list(set([item for sublist in list_of_lists for item in sublist]))

leaves = [i for i in graph if len(graph[i]) == 1]
matchings = []

while leaves:

    # Phase 1:
    # Find all matches
    # Delete all edges from parents to leaves
    # Delete all leaves that are being matched
    # Get a list of parents to look at for round two
    parents = []

    # Go through every leaf found in the beginning
    for leaf in leaves:

        # Get the parent of each leaf
        parent = graph[leaf][0]

        # If the parent has not been matched yet add it and save for Phase 2
        if not parent in listify(matchings):
            matchings += [(leaf,parent)]
            parents += [parent]

            # Sometimes a leave's parent is also a leave for this round
            # If thats the case remove that parent and delete it
            # That can be done because this parent will be looked at as leave
            # anyways
            if parent in leaves:
                leaves.remove(parent)
                del graph[parent]

        # Delete the edge of parent that leads to this leaf
        if leaf in graph[parent]:
            graph[parent].remove(leaf)

        # Delete the leaf because we have used it now
        del graph[leaf]

    # Phase 2:
    # Find all parents of the parents and look for the
    # leaves for the next round. A parent may have more
    # than 1 parent because we can come from different
    # directions
    new_leaves = []

    # Now go through every parent
    for parent in parents:

        # And get the parent's parents
        parent_parents = graph[parent]

        # There can be multiple parents because we can come from
        # Any direction
        for parent_parent in parent_parents:

            # If the parent's parent is not a parent this round
            # it's indeed a leaf for the next round
            if not parent_parent in parents:
                if not parent_parent in new_leaves:
                    new_leaves += [parent_parent]

            # Finally remove the edge from parent_parent to
            # the parent which will be deleted in a second
            graph[parent_parent].remove(parent)

        # Delete the parent because we have all information neede for next phase 1
        del graph[parent]

    leaves = new_leaves