# Introduction

Welcome to the repo of our **"Advanced Programming"** class project.

This project is created and maintained by 

Lucien **LORENZ**  lucien.lorenz@unil.ch
Florent **DABURON**	florent.daburon@unil.ch

The aim of this project is to simulate game theory results to see if the Mixed Strategy Equilibrium is robust to model changes (mutation, and others). The paper associated is attached to the github repo for a complete explanation.

# Getting Started

1. Open the project in your favourite IDE, making sure that the requirements.txt is present to install all necessary packages. When it is done, simply run the main file.
2. If you cannot be bothered with running the program yourself, simply download the file for your platform from the release section (Windows and Linux only).**NOTE:** this program has been developed on Windows, and tested on Windows and Linux (Ubuntu via Windows Subsytem for Linux). It may or may not function on MacOS with the source code as we do not possess such kind of piece of art to work on it. An issue as been indentified with the multi-threading behavior on macs with Apple Silicion.

# Model Parameters and behaviour

A population of *n* players is present on a field with *k* food nodes. Each generation, a player chooses a node randomly. If two players end up on a node, the payoff will depend on each player's type, but if a player ends on a node alone, he gets the default payoff.
If parameters are correct, according to the Game Theory model, you should get a convergence in Mixed Strategies.
In this specification, the next generation is created as follows :
For each player in current generation, check the payoff. If it is between 0 and 1, it might survive. If it is between 1 and 2, it survives and might create an offspring. If it is above 2, it survives for sure, creates an offspring for each integer above 1, and might create another for the remainder.

In the GUI, you will find default parameters to have a basic convergence of 50% Hawk, 50% Dove. However, if you want to check different specifications, you are able to change :

1. The payoff matrix
2. The default payoff (if a player ends on a node alone)
3. The number of generations (simulations)
4. The initial population
5. The maximum population
6. The number of food nodes
7. The maximum population
8. The random seed (for reproducible results)
9. Specifications for model extensions (mutation rate, food search, population culling)

# Model Extensions

## Mutation

If you enable population mutation, when an offspring is created, it might randomly switch types, and you can control the mutation rate for each type separately.

## Food Search

We assume that each player is more or less faster, better, stronger, etc. than their counterpart, which affects their payoff (and theirs only). We also assume that this "upgrade" (or downgrade) follows a Normal Distribution (which you can specify the parameters for each type of player), and is calculated as such :
```math
X \sim \mathcal{N}(\mu, \sigma)
```
```math
\text{payoff}_i = \text{payoff}_{i,matrix} - X
```
## Population Control

If the population hits the cap, it culls the excess randomly by default. However, you can change this to kill the youngest players, or the oldest.

