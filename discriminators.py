"""Logic for dealing with discriminators."""
import collections
from typing import Any, Dict, List, Set

import networkx
from networkx.algorithms import clique

from mcd.techlabs import qsr


def choice_groups(
        products: List[qsr.ProductBase], ix: qsr.ProductIndex,
        binary_choices: Dict[str, List[str]]):
    """
    Find the discriminator choices of a set of products, ie.  of N discriminators
    where each product must have exactly 1 of N.
    Worst-case exponential runtime in the number of discriminators, but
    this is expected to be small.
    """
    base_set: Set[str] = set()
    discriminators = base_set.union(*[p.discriminators for p in products])
    graph = networkx.complete_graph(discriminators)
    name = products[0].base_name

    # if a product has two things, they aren't mutually exclusive
    for p in products:
        p_discriminators = p.discriminators
        # can-adds being other discriminators is treated as not mutually exclusive
        add_names = {ix[c.code].base_name for c in p.can_adds}
        p_discriminators += tuple(
            name for name in add_names if name in discriminators)

        subgraph = networkx.complete_graph(p_discriminators)
        graph.remove_edges_from(subgraph.edges)

    # TODO: This graph algorithm has lots of tricky edge cases, we should
    # refactor it and add lots of unit tests
    choice_sets = []
    while True:
        cliques = list(clique.find_cliques(graph))
        last_clique: Set[Any] = set()
        for i, c in enumerate(cliques):
            # create special whitelisted binary choices
            if (name in binary_choices and list(c)[0] in binary_choices[name] and
                    len(c) == 1):
                last_clique = {list(c)[0], None}
                break

            # otherwise, count how discriminators are distributed over the products
            discriminator_counts: Dict[str, int] = collections.defaultdict(int)
            for p in products:
                p_discriminators = tuple(set(p.discriminators) & set(c))
                if p_discriminators:
                    discriminator_counts[p_discriminators[0]] += 1
                else:
                    discriminator_counts[''] += 1

            # either we're forced to make a choice, or there's one product per choice
            if (discriminator_counts[''] == 0 or
                    max(discriminator_counts.values()) == 1):
                last_clique = c
                if (len(last_clique) > 1 and len(cliques) > i + 1 and
                        len(last_clique) == len(cliques[i + 1])):
                    raise ValueError(
                        "Choice sets %s for discriminator graph %s (%s) are the "
                        "same size, which one gets used will be non-deterministic" %
                        (cliques[i:i + 2], graph.edges, products))
                break

        if last_clique:
            choice_sets.append(last_clique)
            graph.remove_nodes_from(last_clique)
        else:
            break

    return choice_sets