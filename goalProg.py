"""

# - *- coding: utf-8 -*-

Created on Sep 2023

@authors: Angelos & Jorge
"""
# Set the working directory (Replace with your directory path)
import os
os.chdir("D:/spyder")


from ortools.linear_solver import pywraplp

# Function to solve model
def solveModel1(weights):
    
    # Parameters (insert the respective data)------------------------
    
    # 1. Average costs for using each water [$/m3] and energy source [$/kWh]
    Costs = {'GWC':1.5, 'SWC':1.2, 'EC': 0.2, 'ERC': 0.25}
    
    # 2. CO2 emissions [kg CO2] from water and energy production
    Emissions = {'GWE': 0.15, 'SWE': 0.05, 'EE': 0.25, 'ERE': 0.02}       
    
    RHS = {
           'B': 10000.0,    # [$] Budget #1
           'GHG': 4000.0,     # [kg CO2] #2
           'GWA': 2000.0,   # [m3] #3
           'SWA': 1000.0,   # [m3] #4
           'EA': 4500.0,      # [kWh] #5
           'ERA': 3000.0,      # [kWh] #6
           'TWA': 3000.0,         # [m3] #7
           'TEA': 7500.0,      # [kWh] #8
           'WD': 3200.0,     # [m3] #9
           'ED': 8500.0,     # [m3] #10          
           }
    
    # Solver ------------------------------------------------
    solver = pywraplp.Solver.CreateSolver('GLOP')
    
    # Decision variables
    GW = solver.NumVar(0, solver.infinity(), 'GW') # amount of groundwater to use [m3]
    SW = solver.NumVar(0, solver.infinity(), 'SW') # amount of surface water to use [m3]
    E =  solver.NumVar(0, solver.infinity(), 'E') # amount of non-renewable energy to produce [kWh]
    ER = solver.NumVar(0, solver.infinity(), 'ER')  # amount of renewable energy to produce [kWh]
    
    # Deviation (dummy) variables
    d_cost_plus = solver.NumVar(0, solver.infinity(), 'd_cost_plus')
    
    d_emiss_plus = solver.NumVar(0, solver.infinity(), 'd_emiss_plus')
    
    d_gw_plus =  solver.NumVar(0, solver.infinity(), 'd_gw_plus')
    
    d_sw_plus =  solver.NumVar(0, solver.infinity(), 'd_sw_plus')
    d_sw_minus = solver.NumVar(0, solver.infinity(), 'd_sw_minus')
    
    d_e_plus =  solver.NumVar(0, solver.infinity(), 'd_e_plus')  
    
    d_er_minus = solver.NumVar(0, solver.infinity(), 'd_er_minus')
    
    d_w_plus =  solver.NumVar(0, solver.infinity(), 'd_w_plus')
    
    d_en_plus =  solver.NumVar(0, solver.infinity(), 'd_en_plus')  
    
    d_wd_plus =  solver.NumVar(0, solver.infinity(), 'd_wd_plus')
    d_wd_minus = solver.NumVar(0, solver.infinity(), 'd_wd_minus')
    
    d_ed_plus =  solver.NumVar(0, solver.infinity(), 'd_ed_plus')
    d_ed_minus = solver.NumVar(0, solver.infinity(), 'd_ed_minus')
    
    # Constraint 1. Costs [$]
    solver.Add( Costs['GWC']*GW + Costs['SWC']*SW + Costs['EC']*E + Costs['ERC']*ER - d_cost_plus <= RHS['B'] )   
    
    # Constraint 2. CO2 Emissions [kg CO2]
    solver.Add( Emissions['GWE']*GW + Emissions['SWE']*SW + Emissions['EE']*E + Emissions['ERE']*ER - d_emiss_plus <= RHS['GHG'] )
    
    # Constraint 3.  Minimize Groundwater use [m3]
    solver.Add( GW - d_gw_plus <= RHS['GWA'] )   

    # Constraint 4.	Reach Surface water availability [m3]
    solver.Add( SW + d_sw_minus - d_sw_plus >= RHS['SWA'])
    solver.Add( SW + d_sw_minus - d_sw_plus <= RHS['SWA'])
    
    # Constraint 5.	Minimize non-renewable energy production capacity [kWh]
    solver.Add( E - d_e_plus <= RHS['EA'] )
    
    # Constraint 6. Maximize renewable energy production capacity [kWh]
    solver.Add( ER + d_er_minus >= RHS['ERA'] )
    
    # Constraint 7.	Water availability [m3]
    solver.Add( GW + SW - d_w_plus <= RHS['TWA'] )
    
    # Constraint 8.	Energy availability [kWh]
    solver.Add( E + ER - d_en_plus <= RHS['TEA'] )
    
    # Constraint 9.	Meet Water Demand [m3]
    solver.Add( GW + SW - d_wd_plus + d_wd_minus >= RHS['WD'])
    solver.Add( GW + SW - d_wd_plus + d_wd_minus <= RHS['WD'])
    
    # Constraint 10.	Meet Energy Demand [kWh]
    solver.Add( E + ER - d_ed_plus + d_ed_minus >= RHS['ED'])
    solver.Add( E + ER - d_ed_plus + d_ed_minus <= RHS['ED'])
    
    # Objective function
    solver.Minimize(
        weights['Exceed_Cost'] * d_cost_plus +        # 1st constraint
        weights['Exceed_Emissions'] * d_emiss_plus +  # 2nd constraint
        weights['Exceed_GW'] * d_gw_plus +            # 3rd constraint
        weights['Deficit_SW'] * d_sw_minus +          # 4th constraint
        weights['Exceed_SW']  * d_sw_plus +           # 4th constraint
        weights['Exceed_NREnergy'] * d_e_plus +       # 5th constraint
        weights['Deficit_REnergy'] * d_er_minus +     # 6th constraint
        weights['Exceed_TWA'] * d_w_plus +            # 7th constraint
        weights['Exceed_TEA'] * d_en_plus +           # 8th constraint
        weights['Deficit_WD'] * d_wd_minus +          # 9th constraint
        weights['Exceed_WD']  * d_wd_plus +           # 9th constraint
        weights['Deficit_ED'] * d_ed_minus +          # 10th constraint
        weights['Exceed_ED']  * d_ed_plus             # 10th constraint
        )           
    
    
    # Solution -----------------------------------------
    status = solver.Solve()
    
    if status == pywraplp.Solver.OPTIMAL:
        print('\n')  # Leaves a row without printing
        print('Optimal solution found:')
        print('Objective value ($): {0:.3f}'.format( solver.Objective().Value() ))
        print('-----------------------------')
        print('GW (m3) = \t {0:.3f}'.format( GW.solution_value() ))
        print('SW (m3) = \t {0:.3f}'.format( SW.solution_value() ))
        print('E (kWh) = \t {0:.3f}'.format( E.solution_value() ))
        print('ER (kWh) = \t {0:.3f}'.format( ER.solution_value() ))
        print('-----------------------------')
        print('Exceedance of costs ($): {0:.3f}'.format( d_cost_plus.solution_value() ))
        print('Exceedance of emissions (kg CO2): {0:.3f}'.format( d_emiss_plus.solution_value() ))
        print('Exceedance of groundwater use (m3): {0:.3f}'.format( d_gw_plus.solution_value() ))
        print('Exceedance of surface water use (m3): {0:.3f}'.format( d_sw_plus.solution_value() ))
        print('Loss of surface water available to use (m3): {0:.3f}'.format( d_sw_minus.solution_value() ))
        print('Exceedance of non-renewable energy production (kWh): {0:.3f}'.format( d_e_plus.solution_value() ))
        print('Loss of renewable energy available to use (kWh): {0:.3f}'.format( d_er_minus.solution_value() ))
        print('-----------------------------')
        print('Exceedance in water supply (m3): {0:.3f}'.format( d_w_plus.solution_value() ))
        print('Exceedance in energy supply (kWh): {0:.3f}'.format( d_en_plus.solution_value() ))
        print('Exceedance in water demand (m3): {0:.3f}'.format( d_wd_plus.solution_value() ))
        print('less water demand consumed (m3): {0:.3f}'.format( d_wd_minus.solution_value() ))
        print('Exceedance in energy demand (kWh): {0:.3f}'.format( d_ed_plus.solution_value() ))
        print('less energy demand consumed (kWh): {0:.3f}'.format( d_ed_minus.solution_value() ))
        print('-----------------------------')
        
        opt_sol = {var.name():var.solution_value() for var in solver.variables()}
        opt_sol['Obj_fun'] = solver.Objective().Value()
        return opt_sol
    else:
        print('The problem does not have a feasible solution.')
    return None

#      “Intensive Economy” Scenario 

if __name__ == '__main__':
    # Penalization of deviations from target values
    weights = {
        'Exceed_Cost': 0.9,              # $
        'Exceed_Emissions': 0.1,         # kg CO2
        'Exceed_GW': 0.1,                # m3
        'Deficit_SW': 0.1,               # m3
        'Exceed_SW': 0.1,                # m3
        'Exceed_NREnergy': 0.3,          # kWh
        'Deficit_REnergy': 0.5,          # kWh
        'Exceed_TWA': 0.2,               # m3
        'Exceed_TEA': 0.2,               # kWh
        'Deficit_WD': 0.8,               # m3
        'Exceed_WD': 0.8,                # m3
        'Deficit_ED': 0.8,               # kWh
        'Exceed_ED': 0.8,                # kWh
        }
    
    # Call function to solve model
    opt_sol = solveModel1(weights)
    


#      “Middle solution” Scenario 

if __name__ == '__main__':
    # Penalization of deviations from target values
    weights = {
        'Exceed_Cost': 0.5,              # $
        'Exceed_Emissions': 0.4,         # kg CO2
        'Exceed_GW': 0.4,                # m3
        'Deficit_SW': 0.5,               # m3
        'Exceed_SW': 0.5,                # m3
        'Exceed_NREnergy': 0.6,          # kWh
        'Deficit_REnergy': 0.7,          # kWh
        'Exceed_TWA': 0.5,               # m3
        'Exceed_TEA': 0.3,               # kWh
        'Deficit_WD': 0.7,               # m3
        'Exceed_WD': 0.7,                # m3
        'Deficit_ED': 0.6,               # kWh
        'Exceed_ED': 0.6,                # kWh
        }
    
    # Call function to solve model
    opt_sol = solveModel1(weights)




#     “Environmentalist" Scenario 

if __name__ == '__main__':
    # Penalization of deviations from target values
    weights = {
        'Exceed_Cost': 0.2,              # $
        'Exceed_Emissions': 1.0,         # kg CO2
        'Exceed_GW': 0.8,                # m3
        'Deficit_SW': 0.7,               # m3
        'Exceed_SW': 0.7,                # m3
        'Exceed_NREnergy': 0.8,          # kWh
        'Deficit_REnergy': 0.8,          # kWh
        'Exceed_TWA': 0.7,               # m3
        'Exceed_TEA': 0.5,               # kWh
        'Deficit_WD': 0.5,               # m3
        'Exceed_WD': 0.5,                # m3
        'Deficit_ED': 0.4,               # kWh
        'Exceed_ED': 0.4,                # kWh
        }
    
    # Call function to solve model
    opt_sol = solveModel1(weights)




