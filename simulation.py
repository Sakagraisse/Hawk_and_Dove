################
#import libraries and dependencies
################
import numba as nb
import numpy as np
import data_storage as ds

TYPE_DOVE = 0
TYPE_HAWK = 1


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
    total_pop = len(types)
    if nodes < total_pop:
        nodes = total_pop

    positions = np.full(nodes, -1, dtype=np.int64)
    positions[:total_pop] = np.arange(total_pop, dtype=np.int64)
    rng.shuffle(positions)
    positions = positions[: nodes - (nodes % 2)]
    pairs = positions.reshape(-1, 2)

    fitness = np.zeros(total_pop, dtype=np.float64)
    a = pairs[:, 0]
    b = pairs[:, 1]

    mask_a = a >= 0
    mask_b = b >= 0

    idx = (~mask_a) & mask_b
    fitness[b[idx]] = default

    idx = mask_a & (~mask_b)
    fitness[a[idx]] = default

    idx = mask_a & mask_b
    if np.any(idx):
        a_idx = a[idx]
        b_idx = b[idx]
        types_a = types[a_idx]
        types_b = types[b_idx]

        hh = (types_a == TYPE_HAWK) & (types_b == TYPE_HAWK)
        hd = (types_a == TYPE_HAWK) & (types_b == TYPE_DOVE)
        dh = (types_a == TYPE_DOVE) & (types_b == TYPE_HAWK)
        dd = (types_a == TYPE_DOVE) & (types_b == TYPE_DOVE)

        if np.any(hh):
            fitness[a_idx[hh]] = payoffs["hawk / hawk"]
            fitness[b_idx[hh]] = payoffs["hawk / hawk"]
        if np.any(hd):
            fitness[a_idx[hd]] = payoffs["hawk / dove"]
            fitness[b_idx[hd]] = payoffs["dove/hawk"]
        if np.any(dh):
            fitness[a_idx[dh]] = payoffs["dove/hawk"]
            fitness[b_idx[dh]] = payoffs["hawk / dove"]
        if np.any(dd):
            fitness[a_idx[dd]] = payoffs["dove/dove"]
            fitness[b_idx[dd]] = payoffs["dove/dove"]

    return fitness


################
# implements a version of the model where each animal spends time, reducing fitness,
# to search for food
################

def food_search(types, fitness, mean_hawk, shape_hawk, mean_dove, shape_dove, rng):
    """This function handles the special case where types need time to get to the node"""
    hawk_mask = types == TYPE_HAWK
    dove_mask = ~hawk_mask
    if np.any(hawk_mask):
        fitness[hawk_mask] -= rng.normal(loc=mean_hawk, scale=shape_hawk, size=hawk_mask.sum())
    if np.any(dove_mask):
        fitness[dove_mask] -= rng.normal(loc=mean_dove, scale=shape_dove, size=dove_mask.sum())
    return fitness


################
# Compute the next generation of the population
################

#refactoring of selection : this time, if the fitness is superior to 1, the individual
#survives for sure, and creates descendants surely for every floor(integer)-1
#The decimal part can then be created or not
#finally, we check mutation for each new descendant

@nb.njit
def selection2_numba(types, ids, fitness, hawk_to_dove, dove_to_hawk, next_id, seed):
    np.random.seed(seed)
    count = len(types)
    keep = np.zeros(count, dtype=np.bool_)
    extra_count = np.zeros(count, dtype=np.int64)

    for i in range(count):
        fit = fitness[i]
        if fit > 1.0:
            keep[i] = True
            residual = fit - 1.0
            extra = int(residual)
            if np.random.random() < (residual - extra):
                extra += 1
            extra_count[i] = extra
        elif fit == 1.0:
            keep[i] = True
        else:
            if np.random.random() < fit:
                keep[i] = True

    total_new = keep.sum() + extra_count.sum()
    new_types = np.empty(total_new, dtype=np.int8)
    new_ids = np.empty(total_new, dtype=np.int64)
    pos = 0

    for i in range(count):
        if keep[i]:
            new_types[pos] = types[i]
            new_ids[pos] = ids[i]
            pos += 1
        extra = extra_count[i]
        if extra > 0:
            parent_type = types[i]
            for _ in range(extra):
                if parent_type == TYPE_HAWK:
                    mutated = np.random.random() < hawk_to_dove
                    new_types[pos] = TYPE_DOVE if mutated else TYPE_HAWK
                else:
                    mutated = np.random.random() < dove_to_hawk
                    new_types[pos] = TYPE_HAWK if mutated else TYPE_DOVE
                new_ids[pos] = next_id
                next_id += 1
                pos += 1

    return new_types, new_ids, next_id


def selection2(types, ids, fitness, hawk_to_dove=0, dove_to_hawk=0, rng=None, next_id=0):
    """This function handles how the population goes to the next generation"""
    if rng is None:
        rng = np.random.default_rng()
    seed = int(rng.integers(0, 2**31 - 1))
    return selection2_numba(types, ids, fitness, hawk_to_dove, dove_to_hawk, next_id, seed)


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
    total = len(types)
    if total < params["MAX_POP"]:
        return types, ids
    if total >= params["MAX_POP"]:
        target = params["MAX_POP"] - 1
        if params["LIMIT_RANDOM"]:
            indices = rng.permutation(total)[:target]
            return types[indices], ids[indices]
        if params["LIMIT_OLD"]:
            order = np.argsort(ids)
            order = order[:target]
            return types[order], ids[order]
        if params["LIMIT_YOUNG"]:
            order = np.argsort(ids)[::-1]
            order = order[:target]
            return types[order], ids[order]
        raise "ERROR : no method selected for purge"


def rolling_avg(data, window):
    """Calculates the rolling average of a column"""
    effective_window = min(len(data), window)
    return data[len(data) - effective_window :].mean()
