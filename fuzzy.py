# -*- coding: utf-8 -*-
"""
Created on Sep 2023

@author: Angelos
"""

# Step 1: Set the working directory (Replace with your directory path)
import os
os.chdir("D:/spyder")

# Step 2: Import necessary libraries
import numpy as np
from scipy.optimize import linprog

# Step 3:Define the decision variables and coefficients for the objective function
# Decision Variables
# GW: amount of groundwater to use [m3]
# SW: amount of surface water to use [m3]
# E: amount of non-renewable energy to produce [kWh]
# ER: amount of renewable energy to produce [kWh]

# Coefficients for the objective function
c = [GWC, SWC, EC, ERC]

# Step 4: Define the fuzzy parameters for GWA and SWA (manually)
# You can adjust the membership values as needed
alpha_cut_level = 0.5

# Fuzzy set for GWA
GWA_low = 1000  # Low membership value
GWA_medium = 2000  # Medium membership value
GWA_high = 4000  # High membership value

# Fuzzy set for SWA
SWA_low = 500  # Low membership value
SWA_medium = 1000  # Medium membership value
SWA_high = 3000  # High membership value

# Calculate the alpha-cuts for GWA and SWA at the specified alpha_cut_level
TWA_low = min(GWA_low, SWA_low)
TWA_medium = min(GWA_medium, SWA_medium)
TWA_high = min(GWA_high, SWA_high)

# Use TWA_low, TWA_medium, and TWA_high as the total water availability values
TWA = TWA_high  # You can choose a different alpha-cut level if needed


# Step 5: Define the other Parameters (the non-fuzzy ones)
# for water demand
WD = 2700  # Water Demand (total for urban + agriculture) [m3]

# for energy supply
EA = 5000  # Energy production capacity from non-renewable sources (Energy Availability) [kWh]
ERA = 3000  # Energy production capacity from renewable sources (Energy Renewable Availability) [kWh]

# TEA: Total Energy Availability = EA + ERA
TEA = EA + ERA

# for energy demand
ED = 6500  # Energy Demand (total for urban + agriculture) [kWh]

# for costs
GWC = 1.5  # Cost for using groundwater [$/m3]
SWC = 1.2  # Cost for using surface water [$/m3]
EC = 0.2  # Cost for using non-renewable energy [$/kWh]
ERC = 0.25  # Cost for using renewable energy [$/kWh]

B = 12000  # Budget (maximum money available) [$]

# for Carbon emissions
GWE = 0.15  # Groundwater emissions [kg CO2/m3]
SWE = 0.05  # Surface water emissions [kg CO2/m3]
EE = 0.25  # Non-renewable energy emissions [kg CO2/kWh]
ERE = 0.02  # Renewable energy emissions [kg CO2/kWh]

GHG = 4500  # Emissions (maximum allowable CO2 emissions) [kg CO2]

  
# Step 6: Define the constraints
# Initialize the inequality (A_ub) and equality (A_eq) constraint matrices
A_ub = []
A_eq = []

# Initialize the right-hand sides of inequality and equality constraints (b_ub and b_eq)
b_ub = []
b_eq = []

# Water availability constraint: GW + SW <= TWA [m3]
A_ub.append([1, 1, 0, 0])
b_ub.append(TWA)

# Energy availability constraint: E + ER <= TEA [kWh]
A_ub.append([0, 0, 1, 1])
b_ub.append(TEA)

# Water demand constraint: GW + SW = WD [m3]
A_eq.append([1, 1, 0, 0])
b_eq.append(WD)

# Energy demand constraint: E + ER = ED [kWh]
A_eq.append([0, 0, 1, 1])
b_eq.append(ED)

# Carbon emission allowance
A_ub.append([GWE, SWE, EE, ERE])
b_ub.append(GHG)

# Budget available
A_ub.append([GWC, SWC, EC, ERC])
b_ub.append(B)

# Non-renewable energy production capacity: E <= EA [kWh]
A_ub.append([0, 0, 1, 0])
b_ub.append(EA)

# Renewable energy production capacity: ER <= ERA [kWh]
A_ub.append([0, 0, 0, 1])
b_ub.append(ERA)


# Step 7: Convert lists to NumPy arrays
A_ub = np.array(A_ub)
A_eq = np.array(A_eq)
b_ub = np.array(b_ub)
b_eq = np.array(b_eq)


# Step 8: Solve the fuzzy linear program
result = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, method='highs')

# Check if a solution was found and print the results
if result.success:
    print("Optimal Solution Found!")
    print("Objective Function =", result.fun)
    print("Decision Variables:")
    print("GW:", result.x[0], "m3")
    print("SW:", result.x[1], "m3")
    print("E:", result.x[2], "kWh")
    print("ER:", result.x[3], "kWh")
    print("Optimized TWA =", TWA - result.x[0] - result.x[1], "m3, remaining water available (environmental flows)")
    print("Optimized TEA =", TEA - result.x[2] - result.x[3], "kWh, remaining energy available (can be renewable instead of non-renewable)")
    print("Optimized GHG =", GHG - (GWE * result.x[0] + SWE * result.x[1] + EE * result.x[2] + ERE * result.x[3]), "kg CO2, compared to the maximum allowable emissions of 4500 kg CO2 ")   
    print("Optimized Budget =", B - (GWC * result.x[0] + SWC * result.x[1] + EC * result.x[2] + ERC * result.x[3]), "$, compared to the maximum budget of 12000 $")
else:
    print("No feasible solution found. Check your constraints and parameters.")
