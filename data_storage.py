import matplotlib.pyplot as plt

def add_line(liste,results):
    """This function adds a line of statistics to the results dataframe"""
    results.loc[len(results)] = [len(results), liste[0],liste[1], liste[2], liste[3], liste[4]]

def get_plot_2(results):
    """This function plots the relevant dataframe information"""
    fig, axs = plt.subplots(2)

    results[["proportion of dove", "proportion of hawk"]].plot.area(ax=axs[0])
    results[['total population']].plot(ax=axs[1])
    #fig = ax.get_figure()
    return fig




