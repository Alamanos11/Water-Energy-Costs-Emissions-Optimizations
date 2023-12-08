# -*- coding: utf-8 -*-
"""
Created on Sep 2023

@author: Angelos
"""

# Set the working directory (Replace with your directory path)
import os
os.chdir("D:/spyder")

import numpy as np
from scipy.optimize import minimize

# Define the nonlinear cost and emission functions as linear regressions
# These functions represent the coefficients and intercepts obtained from your regressions
def cost_function(x):
    a1, a2, a3, a4 = 0.7, 0.6, 1.0, 1.1     # Replace with your coefficients
    b1, b2, b3, b4 = 200, 50, 300, 40       # Replace with your intercepts
    GW, SW, E, ER = x
    GWC = a1 * GW + b1
    SWC = a2 * SW + b2
    EC = a3 * E + b3
    ERC = a4 * ER + b4
    return GWC * GW + SWC * SW + EC * E + ERC * ER

def emission_function(x):
    c1, c2, c3, c4 = 1.2, 1.0, 1.1, 1.0    # Replace with your coefficients
    d1, d2, d3, d4 = 120, 80, 130, 100     # Replace with your intercepts
    GW, SW, E, ER = x
    GWE = c1 * GW + d1
    SWE = c2 * SW + d2
    EE = c3 * E + d3
    ERE = c4 * ER + d4
    return GWE * GW + SWE * SW + EE * E + ERE * ER

# Define the objective function to minimize (total costs)
def objective(x):
    return cost_function(x)

# Define the constraints
def constraint1(x):
    # Water availability constraint: GW + SW <= TWA
    return x[0] + x[1] - TWA  # Relax constraint1 by subtracting a small epsilon e=100

def constraint2(x):
    # Energy availability constraint: E + ER <= TEA
    return x[2] + x[3] - TEA 

def constraint3(x):
    # Water demand constraint: GW + SW = WD
    return x[0] + x[1] - WD  

def constraint4(x):
    # Energy demand constraint: E + ER = ED
    return x[2] + x[3] - ED  

def constraint5(x):
    # CO2 emissions constraint: GWE * GW + SWE * SW + EE * E + ERE * ER <= GHG
    return emission_function(x) - GHG

def constraint6(x):
    # Budget constraint: GWC * GW + SWC * SW + EC * E + ERC * ER <= B
    return cost_function(x) - B  

def constraint7(x):
    # Groundwater capacity: GW <= GWA
    return x[0] - GWA

def constraint8(x):
    # Surface water capacity: SW = SWA
    return x[1] - SWA

def constraint9(x):
    # Non-renewable energy production capacity: E <= EA
    return x[2] - EA

def constraint10(x):
    # Renewable energy production capacity: ER <= ERA
    return x[3] - ERA

# Define initial guesses for decision variables
# These are guesses for what the optimal solutions might be. 
# Our criterion to gues is the historical knowledge of the problem.
# So, here I put the optimal solutions of the linear model, somewhat increased to get closer to the nonlinear equations.
x0 = np.array([2000, 1200, 5500, 2300])

# Define bounds for decision variables (>= 0)
bounds = [(0, None), (0, None), (0, None), (0, None)]

# Define equality and inequality constraints
constraints = [
    {'type': 'eq', 'fun': constraint1},
    {'type': 'eq', 'fun': constraint2},
    {'type': 'eq', 'fun': constraint3},
    {'type': 'eq', 'fun': constraint4},
    {'type': 'ineq', 'fun': constraint5},
    {'type': 'ineq', 'fun': constraint6},
    {'type': 'eq', 'fun': constraint7},
    {'type': 'eq', 'fun': constraint8},
    {'type': 'eq', 'fun': constraint9},
    {'type': 'eq', 'fun': constraint10},
]

# Define parameters
GWA = 5000  # Groundwater use allowance (Groundwater availability) [m3]
SWA = 4000  # Surface water use allowance (Surface water availability) [m3]
TWA = GWA + SWA  # Total Water Availability
WD = 5000  # water demand [m3]
EA = 8000  # Energy production capacity from non-renewable sources (Energy Availability) [kWh]
ERA = 4000  # Energy production capacity from renewable sources (Energy Renewable Availability)
TEA = EA + ERA   # TEA: Total Energy Availability [kWh]
ED = 6000  # energy demand [kWh]
GHG = 8000  # Maximum allowable CO2 emissions [kg CO2]
B = 18000  # budget [$]

# Solve the nonlinear programming problem
result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints)

# Solve the nonlinear programming problem - If no feasible solution, relax the tolerance to make constraints less strict
result = minimize(objective, x0, method='SLSQP', bounds=bounds, constraints=constraints, tol=1e-6)

# solve with a different method to find feasible solutions
# these ones satified only constraints 5 and 6
result = minimize(objective, x0, method='Nelder-Mead', bounds=bounds, constraints=constraints)
result = minimize(objective, x0, method='L-BFGS-B', bounds=bounds, constraints=constraints)
result = minimize(objective, x0, method='TNC', bounds=bounds, constraints=constraints)


# Print the results
if result.success:
    print("Optimal Solution Found!")
    print("Objective Function (Total Costs) =", result.fun)
    print("Decision Variables:")
    print("GW =", result.x[0], "m^3")
    print("SW =", result.x[1], "m^3")
    print("E =", result.x[2], "kWh")
    print("ER =", result.x[3], "kWh")
    print("---------------------------------------------------")
    print("Constraint Results:")
    for i, constraint in enumerate(constraints):
        constraint_value = constraint['fun'](result.x)
        print(f"Constraint {i + 1}: {constraint_value}")
        if constraint['type'] == 'eq':
            satisfied = abs(constraint_value) < 1e-6  # Check if equality constraint is satisfied
            print(f"Satisfied: {satisfied}")
        else:
            satisfied = constraint_value <= 0  # Check if inequality constraint is satisfied
            print(f"Satisfied: {satisfied}")
        print("---------------------------------------------------")
else:
    print("No feasible solution found. Check your constraints and parameters.")




