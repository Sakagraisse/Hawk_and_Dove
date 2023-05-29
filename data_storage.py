import matplotlib.pyplot as plt
from datetime import datetime

def add_line(liste,results):
    """This function adds a line of statistics to the results dataframe"""
    results.loc[len(results)] = [len(results), liste[0],liste[1], liste[2], liste[3], liste[4],liste[5],liste[6]]

def get_plot_2(results,params):
    """This function plots the relevant dataframe information"""

    fig, axs = plt.subplots(2)
    try:
        expected_equilibrium = 1-(params["PDD"]-params["PHD"])/(params["PHH"]-params["PDH"]+params["PDD"]-params["PHD"])
    except:
        expected_equilibrium = 0
    if expected_equilibrium > 1: expected_equilibrium=1
    elif expected_equilibrium < 0 : expected_equilibrium=0

    results[["proportion of dove", "proportion of hawk"]].plot.area(ax=axs[0])
    results["prop_dove_rolling"].plot(ax=axs[0],label = "Rolling average")
    axs[0].axhline(y=expected_equilibrium, color='red', linestyle='--',label = "Expected Equilibrium")
    axs[0].set_title("Population proportion")
    axs[0].legend(loc = "upper left")
    results[['total population']].plot(ax=axs[1],label = "total population")
    results["total_pop_avg"].plot(ax=axs[1],label = "Rolling average")
    axs[1].set_title("Population growth")
    axs[1].legend(loc = "upper left")
    plt.tight_layout()
    if params["SAVE"]:
        now = datetime.now()
        filename = now.strftime("%H%M%S")
        plt.savefig(f"graph_{filename}.png",dpi=200)

    #fig = ax.get_figure()
    return fig

def get_plot_3(results):
    pass




