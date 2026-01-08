################
#import libraries and dependencies
################
import numpy as np
import os
from juliacall import Main as jl
import data_storage as ds

TYPE_DOVE = 0
TYPE_HAWK = 1
_JULIA_SIM = None


def _get_julia_sim():
    global _JULIA_SIM
    if _JULIA_SIM is None:
        module_path = os.path.join(os.path.dirname(__file__), "julia_simulation.jl")
        jl.include(module_path)
        _JULIA_SIM = jl.HawkDoveSim
    return _JULIA_SIM


def calc_exp(exp_dict, total_ids):
    if total_ids <= 0:
        return 0
    return sum(exp_dict.values()) / total_ids


#Main loop for simulation
#Take parameters from the GUI as input ( default parameters defined in the main.py via the def class for PyQt

def run_sim(params, results):
    """This function handles the simulation"""
    if params["SEED"] < 0:
        rng = np.random.default_rng()
    else:
        rng = np.random.default_rng(params["SEED"])

    payoffs = {
        "hawk / hawk": params["PHH"],
        "hawk / dove": params["PHD"],
        "dove/hawk": params["PDH"],
        "dove/dove": params["PDD"],
    }

    types, ids, next_id = create_initial_pop(params["INITIAL_POP"], params["INITIAL_DOVE"], rng)
    expectancy = {int(id_): 0 for id_ in ids}

    results.loc[0] = [
        0,
        len(types),
        0,
        params["INITIAL_DOVE"],
        1 - params["INITIAL_DOVE"],
        0,
        params["INITIAL_DOVE"],
        len(types),
    ]

    for period in range(1, params["GEN"] + 1):
        fitness = fight(types, params["V_DEF"], params["NODES"], payoffs, rng)
        if params["IS_FOOD_SEARCH"]:
            fitness = food_search(
                types,
                fitness,
                params["HAWK_MEAN"],
                params["HAWK_SHAPE"],
                params["DOVE_MEAN"],
                params["DOVE_SHAPE"],
                rng,
            )

        types, ids, next_id = selection2(
            types,
            ids,
            fitness,
            params["HAWK_MUTATION"],
            params["DOVE_MUTATION"],
            rng,
            next_id,
        )
        types, ids = purge(types, ids, params, rng)
        update_expectancy(ids, expectancy)
        exp_value = calc_exp(expectancy, next_id)
        pop_stats = study_population_basic(types, exp_value, results, params)
        ds.add_line(pop_stats, results)
    return None


def update_expectancy(ids, exp):
    try:
        for id_ in ids:
            key = int(id_)
            exp[key] = exp.get(key, 0) + 1
    except Exception:
        pass


################
#create the initial population
################
# function that create the starting population.
# There is a number of individual set by : number_of_indiv
# and the proportion of dove is set by : number_of_doves

def create_initial_pop(number_of_indiv, number_of_doves, rng):
    """This function creates the initial population with user-defined parameters"""
    total_doves = int(round(number_of_doves * number_of_indiv, 0))
    types = np.empty(number_of_indiv, dtype=np.int8)
    types[:total_doves] = TYPE_DOVE
    types[total_doves:] = TYPE_HAWK
    ids = np.arange(number_of_indiv, dtype=np.int64)
    perm = rng.permutation(number_of_indiv)
    types = types[perm]
    ids = ids[perm]
    next_id = number_of_indiv
    return types, ids, next_id


################
# Calculate the fitness of each individual
################
# We simulate "food nodes" to which the population can go to. If they end up at a node alone, they eat the default value. Otherwise, they fight
# over what is present

def fight(types, default, nodes, payoffs, rng):
    """This function handles interactions between types"""
    sim = _get_julia_sim()
    seed = int(rng.integers(0, 2**31 - 1))
    fitness = sim.fight(
        types,
        float(default),
        int(nodes),
        float(payoffs["hawk / hawk"]),
        float(payoffs["hawk / dove"]),
        float(payoffs["dove/hawk"]),
        float(payoffs["dove/dove"]),
        seed,
    )
    return np.asarray(fitness, dtype=np.float64)


################
# implements a version of the model where each animal spends time, reducing fitness,
# to search for food
################

def food_search(types, fitness, mean_hawk, shape_hawk, mean_dove, shape_dove, rng):
    """This function handles the special case where types need time to get to the node"""
    sim = _get_julia_sim()
    seed = int(rng.integers(0, 2**31 - 1))
    updated = sim.food_search(
        types,
        fitness,
        float(mean_hawk),
        float(shape_hawk),
        float(mean_dove),
        float(shape_dove),
        seed,
    )
    return np.asarray(updated, dtype=np.float64)


################
# Compute the next generation of the population
################

#refactoring of selection : this time, if the fitness is superior to 1, the individual
#survives for sure, and creates descendants surely for every floor(integer)-1
#The decimal part can then be created or not
#finally, we check mutation for each new descendant

def selection2(types, ids, fitness, hawk_to_dove=0, dove_to_hawk=0, rng=None, next_id=0):
    """This function handles how the population goes to the next generation"""
    if rng is None:
        rng = np.random.default_rng()
    sim = _get_julia_sim()
    seed = int(rng.integers(0, 2**31 - 1))
    new_types, new_ids, new_next_id = sim.selection2(
        types,
        ids,
        fitness,
        float(hawk_to_dove),
        float(dove_to_hawk),
        int(next_id),
        seed,
    )
    return (
        np.asarray(new_types, dtype=np.int8),
        np.asarray(new_ids, dtype=np.int64),
        int(new_next_id),
    )


################
# Study population
################
# take the population and return the number of individual, the number of dove and the ratio

def study_population_basic(types, exp, results, params):
    """This function handles the various statistics we track, and returns a list of them"""
    try:
        total = len(types)
        dove_count = int(np.sum(types == TYPE_DOVE))
        window = int(round(params["GEN"] * 0.1, 0))
        rolling_prop = rolling_avg(results["proportion of dove"], window)
        avg_pop = rolling_avg(results["total population"], window)
        try:
            year_t = [
                total,
                dove_count,
                dove_count / total,
                1 - dove_count / total,
                exp,
                rolling_prop,
                avg_pop,
            ]
        except Exception:
            year_t = [total, dove_count, 0, 0, exp, rolling_prop, avg_pop]
        return year_t
    except TypeError:
        return [0, 0, 0, 0, exp, 0, 0]


################
# purge
################
# If the pop is above the limit, choose a method to remove individuals
# check if the pop is above the limit
# use random algorithm by default but can be changed
################ random method
# shuffle the population
# remove the first individuals until the pop is below the limit

def purge(types, ids, params, rng):
    """This function handles the population limit"""
    sim = _get_julia_sim()
    seed = int(rng.integers(0, 2**31 - 1))
    new_types, new_ids = sim.purge(
        types,
        ids,
        int(params["MAX_POP"]),
        bool(params["LIMIT_RANDOM"]),
        bool(params["LIMIT_OLD"]),
        bool(params["LIMIT_YOUNG"]),
        seed,
    )
    return np.asarray(new_types, dtype=np.int8), np.asarray(new_ids, dtype=np.int64)


def rolling_avg(data, window):
    """Calculates the rolling average of a column"""
    effective_window = min(len(data), window)
    return data[len(data) - effective_window :].mean()
