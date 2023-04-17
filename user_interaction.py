#############################################

# This file handles user interaction and model
# assumptions, including variables
#############################################
V = 5
C = 4.5
payoffs = {"hawk / hawk" : V/2 - C, "hawk / dove" : V, "dove/hawk":0,"dove/dove" : V/2}
MAX_POP = 1000
INITIAL_POP = 100
INITIAL_DOVE = 0.5
GEN = 1000
DIV_PROP = 0
SEED = 1
PROG_NAME = "THE POPULATIONATOR v2.0.17"
print(f"Beep boop, initializing program {PROG_NAME}. . . ")
print(f"Model Parameters : \n"
      f"Value of food (normalized) : {V} \n"
      f"Cost of fight (normalized) : {C} \n"
      f"Initial population : {INITIAL_POP}"
      f"Maximum population : {MAX_POP} \n"
      f"Proportion of initial doves : {INITIAL_DOVE} \n"
      f"Length of simulation : {GEN} \n"
      f"Probability for offspring to diverge from parent : {DIV_PROP}\n"
      f"Random seed : {SEED}")

if input("Do you want to change model assumptions (Y/N) ?")== "Y" or "N" == "Y" :
    V = input("Set V (between 1 and 2): ")
    C = input("Set C : ")
    INITIAL_POP = input("Set initial population: ")
    MAX_POP = input("Set maximum population: ")
    INITIAL_DOVE = input("Set initial dove fraction (between 0 and 1): ")
    GEN = input("Set simulation length: ")
    DIV_PROP = input("Set divergence probability")
    SEED = input("Set random seed : ")

# modifier pour jusqu'à grands parents
def get_parameters():
    return {"V":V,"C":C,"INITIAL_POP":INITIAL_POP, "MAX_POP":MAX_POP,
            "INITIAL_DOVE":INITIAL_DOVE,"GEN":GEN,
            "DIV_PROP":DIV_PROP, "SEED":SEED}







