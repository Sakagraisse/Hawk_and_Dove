################
#import libraries and dependencies
################
from random import random, shuffle
from numpy.random import normal
import user_interaction as ui



HAWK_MEAN = 0.01
HAWK_SHAPE = 0.2
DOVE_MEAN = 0
DOVE_SHAPE = 0.5
#TODO : kin-selection (parental benefits / drawbacks)
#TODO : search-and-catch

################
#get parameters and other variables
################
parameters = ui.get_parameters()
payoffs = {"hawk / hawk" :parameters["V"]/2 - parameters["C"], "hawk / dove" : parameters["V"],
           "dove/hawk":0,"dove/dove" : parameters["V"]/2}


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
        if self.type == "hawk":
            self.food_time_params = (HAWK_MEAN,HAWK_SHAPE)
        else:
            self.food_time_params = (DOVE_MEAN,DOVE_SHAPE)

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
    initial_pop = []
    for i in range(number_of_indiv):
        rnd = random()
        if rnd > number_of_doves:
            initial_pop.append(Player("hawk"))
        else:
            initial_pop.append(Player("dove"))
    return initial_pop

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
def fight(to_study, kin :bool =  False):
    if len(to_study) % 2 == 1:
        to_study[-1].fitness = parameters["V"]
        for i in range(0,len(to_study)-1,2):
            if to_study[i].type == "hawk" and to_study[i+1].type == "hawk":
                to_study[i].fitness = payoffs["hawk / hawk"]
                to_study[i+1].fitness = payoffs["hawk / hawk"]
                if kin: kin_selection_HH(to_study[i],to_study[i+1])
            elif to_study[i].type == "hawk" and to_study[i+1].type == "dove":
                to_study[i].fitness = payoffs["hawk / dove"]
                to_study[i+1].fitness = payoffs["dove/hawk"]
                if kin: kin_selection_HD(to_study[i], to_study[i + 1])
            elif to_study[i].type == "dove" and to_study[i+1].type == "hawk":
                to_study[i].fitness = payoffs["dove/hawk"]
                to_study[i+1].fitness = payoffs["hawk / dove"]
                if kin: kin_selection_HD(to_study[i+1], to_study[i])
            else:
                to_study[i].fitness = payoffs["dove/dove"]
                to_study[i+1].fitness = payoffs["dove/dove"]
    else:
        for i in range(0,len(to_study),2):
            if to_study[i].type == "hawk" and to_study[i+1].type == "hawk":
                to_study[i].fitness = payoffs["hawk / hawk"]
                to_study[i+1].fitness = payoffs["hawk / hawk"]
                if kin: kin_selection_HH(to_study[i],to_study[i+1])
            elif to_study[i].type == "hawk" and to_study[i+1].type == "dove":
                to_study[i].fitness = payoffs["hawk / dove"]
                to_study[i+1].fitness = payoffs["dove/hawk"]
                if kin: kin_selection_HD(to_study[i], to_study[i + 1])
            elif to_study[i].type == "dove" and to_study[i+1].type == "hawk":
                to_study[i].fitness = payoffs["dove/hawk"]
                to_study[i+1].fitness = payoffs["hawk / dove"]
                if kin: kin_selection_HD(to_study[i + 1], to_study[i])
            else:
                to_study[i].fitness = payoffs["dove/dove"]
                to_study[i+1].fitness = payoffs["dove/dove"]


    return to_study

################
# implements a version of the model where each animal spends time, reducing fitness,
# to search for food
################
def food_search(population):
    for animal in population:
        animal.fitness -= normal(loc = animal.food_time_params[0],
                                 scale = animal.food_time_params[1])


################
# Kin selection
################
# the assumpution is that if two individuals are brother/sister they will help each other
# this is modelised by a reduction of the cost to fight of half
# this is the same for parents and children
# and one quarter of reduction between grand-parents and grand-children

def kin_selection_HH(player_1 :{Player},player_2 : {Player}):
    if player_1.genealogy[1] == player_2.genealogy[1] or player_1.genealogy[0] == player_2.genealogy[1] \
            or player_1.genealogy[1] == player_2.genealogy[0]:
        player_1.fitness += parameters["C"]/2
        player_2.fitness += parameters["C"]/2
    elif player_1.genealogy[0] == player_2.genealogy[2] or player_1.genealogy[2] == player_2.genealogy[0]:
        player_1.fitness += parameters["C"]/4
        player_2.fitness += parameters["C"]/4

def kin_selection_HD (player_1: {Player}, player_2: {Player}):
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
def selection(pop_t,mutation_rate=0):
    final_array = []
    for i in range(len(pop_t)):
        if random() <= pop_t[i].fitness - 1 :
            test = random()
            if pop_t[i].type == "hawk":
                if test < mutation_rate:
                    new_player = Player("dove")
                    new_player.add_genealogy(pop_t[i])
                    final_array.append(new_player)
                else:
                    new_player = Player("hawk")
                    new_player.add_genealogy(pop_t[i])
                    final_array.append(new_player)
            elif pop_t[i].type == "dove":
                if test < mutation_rate:
                    new_player = Player("hawk")
                    new_player.add_genealogy(pop_t[i])
                    final_array.append(new_player)
                else:
                    new_player = Player("dove")
                    new_player.add_genealogy(pop_t[i])
                    final_array.append(new_player)
        if random() <= pop_t[i].fitness :
            final_array.append(pop_t[i])
    return final_array

################
# Study population
################
# take the population and return the number of individual, the number of dove and the ratio
def study_population_basic(pop_t):
    dove_count = 0
    for j in range(len(pop_t)):
        if pop_t[j].type == "dove" : dove_count += 1
    try:
        year_t = [ len(pop_t) , dove_count , 1-dove_count/len(pop_t) ]
    except:
        year_t = [len(pop_t), dove_count, -1]
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


def serial_killer(pop_t,method="random",limit=parameters["MAX_POP"]):
    if len(pop_t) < limit:
        return pop_t
    else :
        if method == "random":
            shuffle(pop_t)
            pop_t = pop_t[:limit]
            return pop_t

        if method == "oldest" :
            pop_t.sort(key=lambda x: x.ID, reverse=True)
            pop_t = pop_t[:limit]
            return pop_t

        if method == "youngest" :
            pop_t.sort(key=lambda x: x.ID, reverse=False)
            pop_t = pop_t[:limit]
            return pop_t