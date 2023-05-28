################
#import libraries and dependencies
################
from random import random, shuffle , seed
from numpy.random import normal
import data_storage as ds
from collections import Counter
import pandas as pd

import pandas as pd
# Create a player class that give his type : hawk or dove
# id is unique identifier
# fitness is the survival rate of an individual if inferior to 1
class Player :
    ID = 0
    def __init__(self,type):
        self.type = type
        self.id = Player.ID
        Player.ID += 1
        self.fitness = 1


def calc_exp(dict):
    return sum(dict.values())/Player.ID
#Main loop for simulation
#Take parameters from the GUI as input ( default parameters defined in the main.py via the def class for PyQt

def run_sim(params,results):
    """This function handles the simulation"""
    # Set the desired seed for replicability of a random one if negative
    progress = 0
    if params["SEED"] < 0:
        seed()
    else:
        seed(params["SEED"])

    # set up the base payoffs of the hawk and dove game ( also base fitness in this case )
    # payoffs = {"hawk / hawk": 1+params["V"] / 2 - params["C"], "hawk / dove": 1+params["VHD"],
    #            "dove/hawk": 1, "dove/dove": 1+params["VDD"] / 2}
    payoffs = {"hawk / hawk": params["PHH"], "hawk / dove": params["PHD"],
               "dove/hawk": params["PDH"], "dove/dove": params["PDD"]}


    #create the initial population
    pop = create_initial_pop(params["INITIAL_POP"], params["INITIAL_DOVE"])

    expectancy = {}
    for individual in pop :
        expectancy[individual.ID] = 0
    #create the initial line of statistics
    results.loc[0] = [0,len(pop),0,params["INITIAL_DOVE"], 1-params["INITIAL_DOVE"], 0,params["INITIAL_DOVE"],len(pop)]

    # Main loop for simulation
    for period in range(1, params["GEN"]+1):
        progress = progress + period/params["GEN"]
        #pairing and pairwise payoff calculation
        pop = fight(pop, params["V_DEF"] ,params["NODES"],payoffs)
        #add malus for time to catch
        if params["IS_FOOD_SEARCH"]:
            food_search(pop,params["HAWK_MEAN"],
                        params["HAWK_SHAPE"],
                        params["DOVE_MEAN"],
                        params["DOVE_SHAPE"])

        # Create the offspring according to the fitness of each individual
        pop = selection2(pop,params["HAWK_MUTATION"] ,params["DOVE_MUTATION"])
        # Remove excess individuals if needed
        pop = purge(pop,params)
        # store the new line of statistics 
        # create stats
        update_expectancy(pop,expectancy)
        pop_stats = study_population_basic(pop, calc_exp(expectancy),results,params)
        #store
        ds.add_line(pop_stats,results)
    #generate the graph and return it
    graph = ds.get_plot_2(results,params)
    return graph


def update_expectancy(data,exp):
    for individual in data :
        if individual.ID in exp.keys() : exp[individual.ID] += 1
        else : exp[individual.ID] = 1


################
#create the initial population
################
# function that create the starting population.
# There is a number of individual set by : number_of_indiv
# and the proportion of dove is set by : number_of_doves
def create_initial_pop(number_of_indiv, number_of_doves):
    """This function creates the initial population with user-defined parameters"""
    total_doves = int(round(number_of_doves * number_of_indiv,0))
    # Utiliser une liste en compréhension
    return [Player("dove") if i < total_doves else Player("hawk") for i in range(number_of_indiv)]


################
# Calculate the fitness of each individual
################
# We simulate "food nodes" to which the population can go to. If they end up at a node alone, they eat the default value. Otherwise, they fight
# over what is present
def fight(to_study,default,nodes,payoffs):
    """This function handles interactions between types"""
    #the nodes fill the rest of the population ; it means that as long as the population doesn't hit the node cap,
    #they will have opportunity to reproduce freely
    nodes_list = [0]*(nodes-len(to_study))
    temp_list = to_study + nodes_list
    shuffle(temp_list)
    for i in range(0,len(temp_list),2):
        #we first need to check that the pairing is not an empty node with itself
        if temp_list[i] == 0 and temp_list[i+1] == 0:
            pass
        #then if there is a player "by itself", it gets the default value (survive + reproduce)
        elif temp_list[i] == 0 and temp_list[i+1] != 0:
            temp_list[i+1].fitness = default

        elif temp_list[i] != 0 and temp_list[i+1] == 0:
            temp_list[i].fitness = default
        #there is an effective pairing, and fight / cooperation ensues
        elif temp_list[i].type == "hawk" and temp_list[i+1].type == "hawk":
            temp_list[i].fitness = payoffs["hawk / hawk"]
            temp_list[i+1].fitness = payoffs["hawk / hawk"]

        elif temp_list[i].type == "hawk" and temp_list[i+1].type == "dove":
            temp_list[i].fitness = payoffs["hawk / dove"]
            temp_list[i+1].fitness = payoffs["dove/hawk"]
        elif temp_list[i].type == "dove" and temp_list[i+1].type == "hawk":
            temp_list[i].fitness = payoffs["dove/hawk"]
            temp_list[i+1].fitness = payoffs["hawk / dove"]
        else:
            temp_list[i].fitness = payoffs["dove/dove"]
            temp_list[i+1].fitness = payoffs["dove/dove"]
    #removes every node to keep only the population
    final_array = []
    for item in temp_list:
        if item != 0: final_array.append(item)
    return final_array

################
# implements a version of the model where each animal spends time, reducing fitness,
# to search for food
################
def food_search(population,mean_hawk,shape_hawk,mean_dove,shape_dove):
    """This function handles the special case where types need time to get to the node"""
    for animal in population:
        if animal.type == "hawk":
            animal.fitness -= normal(loc = mean_hawk,
                                 scale = shape_hawk)
        else:
            animal.fitness -= normal(loc = mean_dove,
                                 scale = shape_dove)

################
# Compute the next generation of the population
################

#refactoring of selection : this time, if the fitness is superior to 1, the individual
#survives for sure, and creates descendants surely for every floor(integer)-1
#The decimal part can then be created or not
#finally, we check mutation for each new descendant
def selection2(pop_t,dove_to_hawk=0,hawk_to_dove=0):
    """This function handles how the population goes to the next generation"""
    final_array = []
    for individual in pop_t:
        descendants = []
        #for some reason, a fitness of 1 is an edge-case scenario
        if individual.fitness > 1:
            descendants.append(individual)
            residual_fitness = individual.fitness - 1
            for i in range(0,int(residual_fitness)):
                if individual.type == "hawk":
                    if random() < hawk_to_dove : descendants.append(Player("dove"))
                    else: descendants.append(Player("hawk"))
                else:
                    if random() < dove_to_hawk: descendants.append(Player("hawk"))
                    else: descendants.append(Player("dove"))

            if residual_fitness < 1 and random() < residual_fitness :
                if individual.type == "hawk":
                    if random() < hawk_to_dove : descendants.append(Player("dove"))
                    else: descendants.append(Player("hawk"))
                else:
                    if random() < dove_to_hawk : descendants.append(Player("hawk"))
                    else: descendants.append(Player("dove"))

        elif individual.fitness == 1 :
            descendants.append(individual)

        else:
            if random() < individual.fitness : descendants.append(individual)

        final_array = final_array + descendants

    return final_array



################
# Study population
################
# take the population and return the number of individual, the number of dove and the ratio

def study_population_basic(pop_t, exp,results,params):
    """This function handles the various statistics we track, and returns a list of them"""
    pop_counter = Counter(p.type for p in pop_t)
    dove_count = pop_counter["dove"]
    window = int(round(params["GEN"]*0.1,0))
    rolling_prop = rolling_avg(results["proportion of dove"],window)
    avg_pop = rolling_avg(results["total population"],window)
    try:
        year_t = [len(pop_t), dove_count, dove_count/len(pop_t), 1-dove_count/len(pop_t), exp,rolling_prop,avg_pop]
    except:
        year_t = [len(pop_t), dove_count, 0, 0, exp,rolling_prop,avg_pop]
    return year_t

################
# purge
################
# If the pop is above the limit, choose a method to remove individuals
# check if the pop is above the limit
# use random algorithm by default but can be changed
################ random method
# shuffle the population
# remove the first individuals until the pop is below the limit


def purge(pop_t, params):
    """This function handles the population limit"""
    if len(pop_t) < params["MAX_POP"]:
        return pop_t
    else :
        if params["LIMIT_RANDOM"]:
            shuffle(pop_t)
            pop_t = pop_t[:params["MAX_POP"]]
            return pop_t

        elif params["LIMIT_OLD"]:
            pop_t.sort(key=lambda x: x.generation, reverse=True)
            pop_t = pop_t[:params["MAX_POP"]]
            return pop_t

        elif params["LIMIT_YOUNG"]:
            pop_t.sort(key=lambda x: x.generation, reverse=False)
            pop_t = pop_t[:params["MAX_POP"]]
            return pop_t
        else :
            raise"ERROR : no method selected for purge"


def rolling_avg(data,window):
    """Calculates the rolling average of a column"""
    effective_window = min(len(data),window)
    return data[len(data)-effective_window:].mean()