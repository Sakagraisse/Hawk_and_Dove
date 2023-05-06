################
#import libraries and dependencies
################
from random import random, shuffle , seed
from numpy.random import normal
import data_storage as ds
from collections import Counter
import concurrent.futures

import pandas as pd
#Main loop for simulation
#Take parameters from the GUI as input ( default parameters defined in the main.py via the def class for PyQt

def run_sim(params,results):
    # Set the desired seed for replicability of a random one if negative
    progress = 0
    if params["SEED"] < 0:
        seed()
    else:
        seed(params["SEED"])

    # set up the base payoffs of the hawk and dove game ( also base fitness in this case )
    payoffs = {"hawk / hawk": params["V"] / 2 - params["C"], "hawk / dove": params["V"],
               "dove/hawk": 0, "dove/dove": params["V"] / 2}


    #create the initial population
    pop = create_initial_pop(params["INITIAL_POP"], params["INITIAL_DOVE"])

    #create the dataframe to store the results
    # results = pd.DataFrame(columns=["generation", "total population",
    #                                 "population increase %",
    #                                 "proportion of dove", "proportion of hawk"])


    results.loc[0] = [0,len(pop),0,params["INITIAL_DOVE"], 1-params["INITIAL_DOVE"]]

    # Main loop for simulation
    for period in range(1, params["GEN"]+1):
        progress = progress + period/params["GEN"]
        #suffle for pairing
        shuffle(pop)
        #pairing and pairwise payoff calculation
        fight(pop, params["V"] ,payoffs, params["IS_KIN_SELECT"])
        #add malus for time to catch
        if params["IS_FOOD_SEARCH"]:
            food_search(pop,params["HAWK_MEAN"],
                        params["HAWK_SHAPE"],
                        params["DOVE_MEAN"],
                        params["DOVE_SHAPE"])

        # Create the offspring according to the fitness of each individual
        pop = selection(pop,params["HAWK_MUTATION"] ,params["DOVE_MUTATION"])
        # Remove excess individuals if needed
        pop = serial_killer(pop,params)
        # store the new line of statistics 
        # create stats
        pop_stats = study_population_basic(pop)
        #store
        ds.add_line(pop_stats,results)
    #generate the graph and return it
    graph = ds.get_plot_2(results)
    return graph

################
#create the initial population
################
# Create a player class that give his type : hawk or dove
# id is unique identifier
# generation is the generation in which an individual was created
# fitness is the survival rate of an individual if inferior to 1
# the probability to produce an offspring if fitness superior to 1 is fitness - 1
# genealogy is the list of the id of the parents
# genealogy limit is number depth of the genealogy
class Player :
    ID = 0
    def __init__(self,type):
        self.type = type
        self.id = Player.ID
        self.parent = -1
        self.grandparent = -1
        self.generation = 0
        Player.ID += 1
        self.fitness = 1
        self.genealogy = [self.id, self.parent, self.grandparent]

    def add_genealogy(self,parent):
        self.parent = parent.id
        self.grandparent = parent.grandparent
        self.genealogy = [self.id,self.parent,self.grandparent]


################
#create the initial population
################
# function that create the starting population.
# There is a number of individual set by : number_of_indiv
# and the proportion of dove is set by : number_of_doves
def create_initial_pop(number_of_indiv, number_of_doves):
    total_doves = int(round(number_of_doves * number_of_indiv,0))
    # Utiliser une liste en compréhension
    return [Player("dove") if i < total_doves else Player("hawk") for i in range(number_of_indiv)]

################
# track the proportion
################
# to_study is the population to study and is an array
# to_track is the type to track and is a string
def count_type(to_study, to_track):
    count = 0
    for player in to_study:
        if player.type == to_track:
            count += 1
    return count


################
# Calculate the fitness of each individual
################
# the pop should have been shuffled before
# to cases to take into account
# 1) the population is odd
#   in this case one individual is randomly selected and his fitness is set to V
#   the other individuals are paired and the fitness is calculated with the payoffs
# 2) the population is even
#   in this case the individuals are paired and the fitness is calculated with the payoffs

def update_fitness(pair, params_V, payoffs, kin=False):
    i, j = pair
    if i.type == "hawk" and j.type == "hawk":
        i.fitness = payoffs["hawk / hawk"]
        j.fitness = payoffs["hawk / hawk"]
    elif i.type == "hawk" and j.type == "dove":
        i.fitness = payoffs["hawk / dove"]
        j.fitness = payoffs["dove/hawk"]
    elif i.type == "dove" and j.type == "hawk":
        i.fitness = payoffs["dove/hawk"]
        j.fitness = payoffs["hawk / dove"]
    else:
        i.fitness = payoffs["dove/dove"]
        j.fitness = payoffs["dove/dove"]

def fight(to_study, params_V, payoffs, kin=False):
    pairs = [(to_study[i], to_study[i + 1]) for i in range(0, len(to_study), 2)]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(lambda pair: update_fitness(pair, params_V, payoffs, kin), pairs)

    return to_study
#
# def fight(to_study,params_V,payoffs, kin :bool =  False):
#     if len(to_study) % 2 == 1:
#         to_study[-1].fitness = params_V
#         for i in range(0,len(to_study)-1,2):
#             if to_study[i].type == "hawk" and to_study[i+1].type == "hawk":
#                 to_study[i].fitness = payoffs["hawk / hawk"]
#                 to_study[i+1].fitness = payoffs["hawk / hawk"]
#                 if kin: kin_selection_HH(to_study[i],to_study[i+1])
#             elif to_study[i].type == "hawk" and to_study[i+1].type == "dove":
#                 to_study[i].fitness = payoffs["hawk / dove"]
#                 to_study[i+1].fitness = payoffs["dove/hawk"]
#                 if kin: kin_selection_HD(to_study[i], to_study[i + 1])
#             elif to_study[i].type == "dove" and to_study[i+1].type == "hawk":
#                 to_study[i].fitness = payoffs["dove/hawk"]
#                 to_study[i+1].fitness = payoffs["hawk / dove"]
#                 if kin: kin_selection_HD(to_study[i+1], to_study[i])
#             else:
#                 to_study[i].fitness = payoffs["dove/dove"]
#                 to_study[i+1].fitness = payoffs["dove/dove"]
#     else:
#         for i in range(0,len(to_study),2):
#             if to_study[i].type == "hawk" and to_study[i+1].type == "hawk":
#                 to_study[i].fitness = payoffs["hawk / hawk"]
#                 to_study[i+1].fitness = payoffs["hawk / hawk"]
#                 if kin: kin_selection_HH(to_study[i],to_study[i+1])
#             elif to_study[i].type == "hawk" and to_study[i+1].type == "dove":
#                 to_study[i].fitness = payoffs["hawk / dove"]
#                 to_study[i+1].fitness = payoffs["dove/hawk"]
#                 if kin: kin_selection_HD(to_study[i], to_study[i + 1])
#             elif to_study[i].type == "dove" and to_study[i+1].type == "hawk":
#                 to_study[i].fitness = payoffs["dove/hawk"]
#                 to_study[i+1].fitness = payoffs["hawk / dove"]
#                 if kin: kin_selection_HD(to_study[i + 1], to_study[i])
#             else:
#                 to_study[i].fitness = payoffs["dove/dove"]
#                 to_study[i+1].fitness = payoffs["dove/dove"]
#
#
#     return to_study

################
# implements a version of the model where each animal spends time, reducing fitness,
# to search for food
################
def food_search(population,mean_hawk,shape_hawk,mean_dove,shape_dove):
    for animal in population:
        if animal.type == "hawk":
            animal.fitness -= normal(loc = mean_hawk,
                                 scale = shape_hawk)
        else:
            animal.fitness -= normal(loc = mean_dove,
                                 scale = shape_dove)
################
# Kin selection
################
# the assumpution is that if two individuals are brother/sister they will help each other
# this is modelised by a reduction of the cost to fight of half
# this is the same for parents and children
# and one quarter of reduction between grand-parents and grand-children

def kin_selection_HH(player_1 :{Player},player_2 : {Player},parameters):
    if player_1.genealogy[1] == player_2.genealogy[1] or player_1.genealogy[0] == player_2.genealogy[1] \
            or player_1.genealogy[1] == player_2.genealogy[0]:
        player_1.fitness += parameters["C"]/2
        player_2.fitness += parameters["C"]/2
    elif player_1.genealogy[0] == player_2.genealogy[2] or player_1.genealogy[2] == player_2.genealogy[0]:
        player_1.fitness += parameters["C"]/4
        player_2.fitness += parameters["C"]/4

def kin_selection_HD (player_1: {Player}, player_2: {Player}, parameters):
    if player_1.genealogy[1] == player_2.genealogy[1] or player_1.genealogy[0] == player_2.genealogy[1] \
            or player_1.genealogy[1] == player_2.genealogy[0]:
        player_1.fitness -= parameters["C"]/4
        player_2.fitness += parameters["C"]/4
    elif player_1.genealogy[0] == player_2.genealogy[2] or player_1.genealogy[2] == player_2.genealogy[0]:
        player_1.fitness -= parameters["C"]/8
        player_2.fitness += parameters["C"]/8





################
# Compute the next generation of the population
################
# if the fitness is superior to 1, the individual has a probability of 1 - fitness to produce an offspring
# if the fitness is inferior to 1, the individual has a probability of fitness survive to the next generation
# if the individual is selected to produce an offspring, the the probability to produc an offspring of the othertype
# is mutation_rate
def selection(pop_t,dove_to_hawk=0,hawk_to_dove=0):
    #create the array to return
    final_array = []
    # for each individual, we compute if it survives to the next generation
    # if yes, compute if it produces an offspring
    for i in range(len(pop_t)):
        # if the fitness is superior to 1
        if random() <= pop_t[i].fitness - 1 :
            test = random()
            if pop_t[i].type == "hawk":
                if test < hawk_to_dove:
                    new_player = Player("dove")
                    new_player.add_genealogy(pop_t[i])
                    final_array.append(new_player)
                else:
                    new_player = Player("hawk")
                    new_player.add_genealogy(pop_t[i])
                    final_array.append(new_player)
            elif pop_t[i].type == "dove":
                if test < dove_to_hawk:
                    new_player = Player("hawk")
                    new_player.add_genealogy(pop_t[i])
                    final_array.append(new_player)
                else:
                    new_player = Player("dove")
                    new_player.add_genealogy(pop_t[i])
                    final_array.append(new_player)
        if random() <= pop_t[i].fitness:
            final_array.append(pop_t[i])
    return final_array

################
# Study population
################
# takes the population and returns useful data during this iteration
#generation number, number of doves, proportion of doves and hawks respectively

def study_population_basic(pop_t):
    pop_counter = Counter(p.type for p in pop_t)
    dove_count = pop_counter["dove"]
    try:
        year_t = [len(pop_t), dove_count, dove_count/len(pop_t), 1-dove_count/len(pop_t)]
    except:
        year_t = [len(pop_t), dove_count, 0, 0]
    return year_t

################
# serial killer
################
# If the pop is above the limit, choose a method to remove individuals
# check if the pop is above the limit
# use random algorithm by default but can be changed
################ random method
# shuffle the population
# remove the first individuals until the pop is below the limit


def serial_killer(pop_t, params):
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
            print("ERROR : no method selected for serial killer")