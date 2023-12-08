# -*- coding: utf-8 -*-
"""
Created on Sep 2023

@author: Angelos
"""

# Set the working directory (Replace with your directory path)
import os
os.chdir("D:/spyder")

# Import Necessary Libraries:
import numpy as np
from scipy.optimize import linprog

# Define the Time Horizon (T)
T = 12  # Set the time horizon to 12 months

# Step 2: Create Lists for Decision Variables, Coefficients, and Constraints
decision_vars = []  # To store decision variables (GW, SW, E, ER) for each time step
coefficients = []   # To store coefficients (GWC, SWC, EC, ERC) for the objective function
A_ub_list = []      # To store inequality constraint matrices for each time step
b_ub_list = []      # To store inequality constraint vectors for each time step
A_eq_list = []      # To store equality constraint matrices for each time step
b_eq_list = []      # To store equality constraint vectors for each time step

# Manually Input Time-Dependent Parameters (Monthly Values from January-December)
#              JAN   FEB  MAR   APR    MAY   JUN   JUL  AUG  SEP  OCT   NOV   DEC
GWA_values = [2200, 2200, 2200, 2100, 1900, 1600, 900, 500, 600, 1000, 1500, 2000]  # Groundwater availability [m3]
SWA_values = [1700, 1800, 1600, 1300, 1000, 900,  700, 500, 600, 900,  1200, 1800]  # Surface water availability [m3]
WD_values = [2000, 2100, 2000, 2300, 2400, 2500, 2600, 2700, 2500, 2300, 2000, 2000]  # Water demand [m3]
ERA_values = [3300, 3400, 3200, 3100, 3000, 2700, 2600, 2600, 2800, 3000, 3000, 3000]  # Renewable energy availability [kWh]
EA_values = [5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000, 5000] # Energy production capacity from non-renewable sources (Energy Availability) [kWh]
ED_values = [6500, 6500, 6500, 6500, 6500, 6500, 6500, 6500, 6500, 6500, 6500, 6500]  # Energy Demand (total for urban + agriculture) [kWh]

# for Costs
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

for t in range(T):
    GWA_t = GWA_values[t]
    SWA_t = SWA_values[t]
    WD_t = WD_values[t]
    ERA_t = ERA_values[t]
    EA_t = EA_values[t]
    ED_t = ED_values[t] 
    
    # Total Water Availability & Total Energy Availability
    TWA_t = GWA_t + SWA_t
    TEA_t = EA_t + ERA_t

    # Initialize the inequality (A_ub) and equality (A_eq) constraint matrices for this time step
    A_ub_t = []
    A_eq_t = []

    # Initialize the right-hand sides of inequality and equality constraints (b_ub and b_eq) for this time step
    b_ub_t = []
    b_eq_t = []

    # Water availability constraint: GWt + SWt <= TWAt [m3]
    A_ub_t.append([1, 1, 0, 0])
    b_ub_t.append(TWA_t)

    # Energy availability constraint: Et + ERt <= TEAt [kWh]
    A_ub_t.append([0, 0, 1, 1])
    b_ub_t.append(TEA_t)

    # Water demand constraint: GWt + SWt = WDt [m3]
    A_eq_t.append([1, 1, 0, 0])
    b_eq_t.append(WD_t)

    # Energy demand constraint: Et + ERt = EDt [kWh]
    A_eq_t.append([0, 0, 1, 1])
    b_eq_t.append(ED_t)

    # CO2 emissions constraint: GWE*GWt + SWE*SWt + EE*Et + ERE*ERt <= GHG [kg CO2]
    A_ub_t.append([GWE, SWE, EE, ERE])
    b_ub_t.append(GHG)

    # Budget constraint: GWC*GWt + SWC*SWt + EC*Et + ERC*ERt <= B [$]
    A_ub_t.append([GWC, SWC, EC, ERC])
    b_ub_t.append(B)

    # Groundwater capacity: GWt <= GWAt [m3]
    A_ub_t.append([1, 0, 0, 0])
    b_ub_t.append(GWA_t)

    # Surface water capacity: SWt = SWAt [m3]
    A_eq_t.append([0, 1, 0, 0])
    b_eq_t.append(SWA_t)

    # Non-renewable energy production capacity: Et <= EAt [kWh]
    A_ub_t.append([0, 0, 1, 0])
    b_ub_t.append(EA_t)

    # Renewable energy production capacity: ERt <= ERAt [kWh]
    A_ub_t.append([0, 0, 0, 1])
    b_ub_t.append(ERA_t)

    # Append the constraint matrices and vectors to respective lists for this time step
    A_ub_list.append(A_ub_t)
    b_ub_list.append(b_ub_t)
    A_eq_list.append(A_eq_t)
    b_eq_list.append(b_eq_t)

# Step 4: Convert Lists to NumPy Arrays
A_ub_list = np.array(A_ub_list)
b_ub_list = np.array(b_ub_list)
A_eq_list = np.array(A_eq_list)
b_eq_list = np.array(b_eq_list)


# Step 5: Define the Objective Function
c = []  # Initialize the coefficients for the objective function

# Loop through each time step to calculate the objective function
for t in range(T):
    # Add the coefficients for this time step (GWC*GW_t + SWC*SW_t + EC*E_t + ERC*ER_t)
    c_t = [GWC, SWC, EC, ERC]
    c.extend(c_t)

# Convert the list of coefficients to a NumPy array
c = np.array(c)

# The number of decision variables per time step
num_decision_vars_per_step = 4  # GW, SW, E, ER

# Reshape c to match the dimensions of constraint matrices
c = c.reshape((T, num_decision_vars_per_step))

# Step 6: Solve the Dynamic Optimization Problem for Each Time Step
for t in range(T):
    A_ub_t = A_ub_list[t]
    b_ub_t = b_ub_list[t]
    A_eq_t = A_eq_list[t]
    b_eq_t = b_eq_list[t]

    # Solve the linear program for this time step
    result = linprog(c[t], A_ub=A_ub_t, b_ub=b_ub_t, A_eq=A_eq_t, b_eq=b_eq_t, method='highs')


# Print the results for this time step (t = T = 12)
    print(f"Time Step {t + 1} Results:")
    if result.success:
        print("Optimal Solution Found!")
        print("Objective Function =", result.fun)
        print("Decision Variables:")
        for i, var_name in enumerate(decision_vars):
            print(f"{var_name}: {result.x[i]}")
        # Print other relevant results for this time step
        print(f"Total Water Availability (TWA_t): {TWA_t} m^3")
        print(f"Total Energy Availability (TEA_t): {TEA_t} kWh")
        print(f"Surface Water Availability (SWA_t): {SWA_t} m^3")
        print(f"Groundwater Availability (GWA_t): {GWA_t} m^3")
        print(f"Energy Capacity (EA_t): {EA_t} kWh")
        print(f"Renewable Energy Availability (ERA_t): {ERA_t} kWh")
        # Add more as needed
    else:
        print(f"No feasible solution found for Time Step {t + 1}. Check your constraints and parameters.")
    print("\n")

# Print the results for any other time step

decision_vars = [['GW_t1', 'SW_t1', 'E_t1', 'ER_t1'],
                 ['GW_t2', 'SW_t2', 'E_t2', 'ER_t2'],
                 ['GW_t3', 'SW_t3', 'E_t3', 'ER_t3'],
                 ['GW_t4', 'SW_t4', 'E_t4', 'ER_t4'],
                 ['GW_t5', 'SW_t5', 'E_t5', 'ER_t5'],
                 ['GW_t6', 'SW_t6', 'E_t6', 'ER_t6'],
                 ['GW_t7', 'SW_t7', 'E_t7', 'ER_t7'],
                 ['GW_t8', 'SW_t8', 'E_t8', 'ER_t8'],
                 ['GW_t9', 'SW_t9', 'E_t9', 'ER_t9'],
                 ['GW_t10', 'SW_t10', 'E_t10', 'ER_t10'],
                 ['GW_t11', 'SW_t11', 'E_t11', 'ER_t11'],
                 ['GW_t12', 'SW_t12', 'E_t12', 'ER_t12'],
                ]

# Define the time step you want to analyze (e.g., time step 6)
desired_time_step = 6

# Print the results for the desired time step
if result.success:
    print(f"Optimal Sets of Solutions Found for Time Step {desired_time_step}!")
    print("Objective Function =", result.fun)
    print("Decision Variables:")
    t = desired_time_step - 1  # Adjust for 0-based indexing
    for i, var_name in enumerate(decision_vars[t]):
        print(f"{var_name}: {result.x[i]}")
        # Print other relevant results for this time step
        print(f"Total Water Availability (TWA_t): {TWA_t} m^3")
        print(f"Total Energy Availability (TEA_t): {TEA_t} kWh")
        print(f"Surface Water Availability (SWA_t): {SWA_t} m^3")
        print(f"Groundwater Availability (GWA_t): {GWA_t} m^3")
        print(f"Energy Capacity (EA_t): {EA_t} kWh")
        print(f"Renewable Energy Availability (ERA_t): {ERA_t} kWh")
        # Add more as needed
else:
    print(f"No feasible solution found for Time Step {desired_time_step}. Check your constraints and parameters.")

