import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from random import random, seed, shuffle
import time
seed(2)

V = 1.5
C = 1.2
payoffs = {"hawk / hawk" : V/2 - C, "hawk / dove" : V, "dove/hawk":0,"dove/dove" : V/2}
#create player class
class Player :
    ID = 0
    def __init__(self, type):
        self.type = type
        self.id = Player.ID
        Player.ID += 1
        self.fitness = 1




################
#create database
################
population = np.empty((1,1),Player)
MAX_POP = 1000
INITIAL_POP = 100
INITIAL_DOVE = 0.5
GEN = 100


results = pd.DataFrame(columns = ["generation","total population", "population increase %", "proportion of dove", "number of deaths"])

# creating the initial population
for i in range(INITIAL_POP):
    rnd = random()
    if rnd > INITIAL_DOVE:
        np.append(population,Player("hawk"))
    else:
        np.append(population,Player("dove"))
print(population)
#
# def count_type(population, type):
#     count = 0
#     for player in population:
#         if player.type == type:
#             count += 1
#     return count
#
# #functions for simulation
#
# def fight() :
#     if population.shape[0] % 2 == 1:
#         population[-1].fitness = V
#         for i in range(0,population.shape[0]-1,2):
#             if population[i].type == "hawk" and population[i+1].type == "hawk":
#                 population[i].fitness += payoffs["hawk / hawk"]
#                 population[i+1].fitness += payoffs["hawk / hawk"]
#             elif population[i].type == "hawk" and population[i+1].type == "dove":
#                 population[i].fitness += payoffs["hawk / dove"]
#                 population[i+1].fitness += payoffs["dove/hawk"]
#             elif population[i].type == "dove" and population[i+1].type == "hawk":
#                 population[i].fitness += payoffs["dove/hawk"]
#                 population[i+1].fitness += payoffs["hawk / dove"]
#             else :
#                 population[i].fitness += payoffs["dove/dove"]
#                 population[i+1].fitness += payoffs["dove/dove"]
#     else:
#         for i in range(0,population.shape[0],2):
#             if population[i].type == "hawk" and population[i+1].type == "hawk":
#                 population[i].fitness += payoffs["hawk / hawk"]
#                 population[i+1].fitness += payoffs["hawk / hawk"]
#             elif population[i].type == "hawk" and population[i+1].type == "dove":
#                 population[i].fitness += payoffs["hawk / dove"]
#                 population[i+1].fitness += payoffs["dove/hawk"]
#             elif population[i].type == "dove" and population[i+1].type == "hawk":
#                 population[i].fitness += payoffs["dove/hawk"]
#                 population[i+1].fitness += payoffs["hawk / dove"]
#             else :
#                 population[i].fitness += payoffs["dove/dove"]
#                 population[i+1].fitness += payoffs["dove/dove"]
#
# def selection(pop_array , results):
#     number_deaths = 0
#     final_array = np.empty((1,1))
#     dove_count = 0
#     for i in range(pop_array.shape[0]):
#         if random() <= pop_array[i].fitness - 1 :
#             np.append(final_array,Player(pop_array[i].type))
#         if random() <= pop_array[i].fitness :
#             np.append(final_array,pop_array[i])
#         else:
#             number_deaths += 1
#
#
#     final_array = thanos_snap(final_array)
#     for j in range(final_array.shape[0]):
#         if final_array[j].type == "dove" : dove_count += 1
#
#     results.loc[len(results)] =[len(results),final_array.shape[0],
#                                 final_array.shape[0] / pop_array.shape[0] * 100,
#                                 dove_count / final_array.shape[0] * 100,
#                                 number_deaths]
#     return final_array
#
# # shuffle and cut above a certain number which is the max population
# def thanos_snap(population):
#     np.random.shuffle(population)
#     population = population[:MAX_POP]
#     return population
#
# #simulation
# tic = time.perf_counter()
# for period in range(GEN):
#     np.random.shuffle(population)
#     fight()
#     population = selection(population, results)
# toc = time.perf_counter()
#
#
# print(results)
# print(f"Time to execute : {toc-tic:0.4f} seconds")
# # graph simulation from results dataframe
# results.plot(x = "generation" , y = "proportion of dove", kind = "scatter")
# plt.show()
#
