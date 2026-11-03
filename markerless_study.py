# -*- coding: utf-8 -*-
"""
Created on Tue Nov  3 09:52:48 2026

@author: ronne
"""


import numpy as np
from OLBC_main import OLBC_solver, OLBC_model
from scipy.interpolate import CubicSpline
import pandas as pd
from utils import NRMSE_and_RMSE, plot_BA, solution_dict_to_x0, solution_to_dict, sliding_windows, recombine_windows
import matplotlib.pyplot as plt
from utils import recombine_windows
from utils import plot_res_type_2




# =============================================================================
# Functions
# =============================================================================

def run_in_2_folds(scenario_name, config):
    
    ## Define a fisrt model with full steering and litte points
    
    model_1 = OLBC_model(path_scenario, scenario_name, config)
    
    model_1.initialize_model(config['bike'])
    
    problem_1 = OLBC_solver(model_1, config = config)
    problem_1.solve_and_save()
    previous_solution = problem_1.solution.reshape(model_1.x0_shape)
    # problem_1.plot_res_type_1(0, '', 'fig')
    
    ## Define a second model with more points
    if True:
        config['N_sampling'] = 1
        model_2 = OLBC_model(path_scenario, scenario_name, config)
        model_2.initialize_model(config['bike'])
        
        x0 = np.zeros(model_2.x0_shape)
        
        for i in range(previous_solution.shape[0]):
            x0_i_interpolated = CubicSpline(model_1.x_meas_dict['time'], previous_solution[i, :])
            x0[i, :] = x0_i_interpolated(model_2.x_meas_dict['time'])
        
        problem_2 = OLBC_solver(model_2, x0.flatten(), config = config)
        path_to_results = problem_2.solve_and_save()
        previous_solution = problem_2.solution.reshape(model_2.x0_shape)
        problem_2.plot_res_type_1(0, '', 'fig')
    
    ## Define a new model that include roll control as well
    if False:
        config['roll_control'] = True
        model_3 = OLBC_model(path_scenario, scenario_name, config)
        model_3.initialize_model(config['bike'])
        # model_3.eoms= model_3.eoms*10
            
        x0 = np.zeros(model_3.x0_shape)
        x0[:previous_solution.shape[0], :] = previous_solution
        problem_3 = OLBC_solver(model_3, 1, x0.flatten(), config)
        problem_3.problem.add_option('tol' , 10e-8)
        problem_3.problem.add_option('constr_viol_tol' , 10e-6)
        problem_3.problem.add_option('acceptable_tol' , 10e-6)
        problem_3.solve_and_save()
        problem_3.plot_res_type_1(0, '', 'fig')
        
    return(path_to_results)



    

    
    










config = {
          'K_angles' : 10*2*8*20,
          'K_angles_rates' : 10*2*8*10,
          'K_efforts' : 0.001*0,
          'K_regu' : 0.001,
          'K_speed' : 10000,
          
          'roll_control' : False,
          'steer_torque' : True,
          'N_sampling' : 1,
          'filtering' : {'use_filtering' : False,
                         'low_cut_freq' : 0.01,
                         'high_cut_freq' : 5},
          'validation_data' : 'synthetic',
          'ti': 0,
          'tf': 5,
          'bike': 'Browser',
          'Fy' : False,
          }







if True:
    
    path_scenario = 'D:/Users/ronne/Documents/4_side_quest/OpenLoopBalanceControl/data/markerless/'

    # Benja you need a folder named 'states_kf_gopro_test_1_1' at 'path_scenario'
    # Then rename the csv file "states_and_torques.csv'
    # Add a time vector 
    # Convert to rads
    # remane columns using q1,...,q8, u1 to u8 + 'speed' that is u6*R_r
    # Try to run !
    scenario_name = 'states_kf_gopro_test_1_1'

    path_to_results = run_in_2_folds(scenario_name, config)
    

    
    

