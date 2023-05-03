import matplotlib.pyplot as plt

def add_line(liste,results):
    results.loc[len(results)] = [len(results), liste[0],liste[1], liste[2], liste[3]]

def get_plot(results,absciss="generation",ordonate="proportion of dove", type = "line"):
    #results.plot(x = absciss, y = ordonate, kind = type)
    results[["proportion of dove", "proportion of hawk"]].plot.area()
    plt.show()

def get_plot_2(results, absciss="generation", ordinate="proportion of dove", type="line"):
    #ax = results.plot(x=absciss, y=ordinate, kind=type)
    fig, axs = plt.subplots(2)

    results[["proportion of dove", "proportion of hawk"]].plot.area(ax=axs[0])
    results[['total population']].plot(ax=axs[1])
    #fig = ax.get_figure()
    return fig




