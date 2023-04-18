from random import seed, shuffle
import time
import data_storage as ds
import simulation as sim
import user_interaction as ui
import matplotlib.pyplot as plt
import plotly.graph_objects as go

parameters = ui.get_parameters()
seed(parameters["SEED"])
#TODO : Add input for thanos snap method
#TODO : complexify fight
#TODO : dynamic plot
#TODO : PyQT
#TODO : add different style of fight


# # Create a new plot
# fig, ax = plt.subplots()
#
# # Set the x and y labels
# ax.set_xlabel('Generation')
# ax.set_ylabel('Hawk Proportion')
#
# # Set the x and y limits
# ax.set_xlim(0, 100)
# ax.set_ylim(0, 1)
#
# # Show the plot
# #plt.show()
#
# plt.close()

#acivate differente models over the standard one
kin_selection_toggle = False
miam_miam = True
did_a_mistake = 0

#simulation
pop = sim.create_initial_pop(parameters["INITIAL_POP"],parameters["INITIAL_DOVE"])
tic = time.perf_counter()
for period in range(1,parameters["GEN"]):
    shuffle(pop)
    sim.fight(pop,kin_selection_toggle)
    if miam_miam : sim.food_search(pop)
    pop = sim.selection(pop, did_a_mistake)
    pop = sim.serial_killer(pop)
    pop_stats = sim.study_population_basic(pop)
    ds.add_line(pop_stats)


toc = time.perf_counter()

ds.get_plot()

#pyqt essaie flo.
#We implement

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

