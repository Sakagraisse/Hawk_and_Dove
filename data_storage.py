

# def df_results():
#     results = pd.DataFrame(columns=["generation","total population",
#                                     "population increase %",
#                                     "proportion of dove"])

#parameters = ui.get_parameters()

# def get_results():
#     return results

# liste has 3 arguments
def add_line(liste,results):
    results.loc[len(results)] = [len(results), liste[0],liste[1], liste[2]]

def get_plot(results,absciss="generation",ordonate="proportion of dove", type = "scatter"):
    results.plot(x = absciss, y = ordonate, kind = type)
    plt.show()


import matplotlib.pyplot as plt

def get_plot_2(results, absciss="generation", ordinate="proportion of dove", type="scatter"):
    ax = results.plot(x=absciss, y=ordinate, kind=type)
    fig = ax.get_figure()
    return fig

#############################################
# Graph dynamic plot
#############################################
#create a dynamic plot the print the evolution of the population from generation to generation
# it uses pop as a global variable and print the proportion of doves and hawks

# def create_plot(params):
#     # Initialize the plot
#     fig, ax = plt.subplots()
#     ax.set_xlabel('Generation')
#     ax.set_ylabel('Hawk Proportion')
#     ax.set_xlim(0, params("GEN"))
#     ax.set_ylim(0, 1)
#     plt.title["Evolution of the population"]




