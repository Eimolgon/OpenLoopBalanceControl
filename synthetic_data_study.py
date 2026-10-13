# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 19:00:37 2026

@author: ronne
"""
import numpy as np
from OLBC_main import OLBC_solver, OLBC_model
from scipy.interpolate import CubicSpline
import pandas as pd
from utils import RMSE, plot_BA
# import seaborn as sns
import matplotlib.pyplot as plt



path_scenario = 'D:/Users/ronne/Documents/4_side_quest/OpenLoopBalanceControl/data/synthetic/'


# =============================================================================
# Functions
# =============================================================================

def run_in_2_folds(scenario_name, config):
    
    ## Define a fisrt model with full steering and litte points
    
    model_1 = OLBC_model(path_scenario, scenario_name, config)
    
    model_1.initialize_model()
    
    problem_1 = OLBC_solver(model_1, 1)
    problem_1.solve_and_save()
    previous_solution = problem_1.solution.reshape(model_1.x0_shape)
    problem_1.plot_res_type_1(0, '', 'fig')
    
    ## Define a second model with more points
    if True:
        config['N_sampling'] = 1
        model_2 = OLBC_model(path_scenario, scenario_name, config)
        model_2.initialize_model()
        
        x0 = np.zeros(model_2.x0_shape)
        
        for i in range(previous_solution.shape[0]):
            x0_i_interpolated = CubicSpline(model_1.x_meas_dict['time'], previous_solution[i, :])
            x0[i, :] = x0_i_interpolated(model_2.x_meas_dict['time'])
        
        problem_2 = OLBC_solver(model_2, 1, x0.flatten())
        problem_2.solve_and_save()
        previous_solution = problem_2.solution.reshape(model_2.x0_shape)
        problem_2.plot_res_type_1(1, '', 'fig')
    
    ## Define a new model that include roll control as well
    if False:
        config['roll_control'] = True
        model_3 = OLBC_model(path_scenario, scenario_name, config)
        model_3.initialize_model()
        # model_3.eoms= model_3.eoms*10
            
        x0 = np.zeros(model_3.x0_shape)
        x0[:previous_solution.shape[0], :] = previous_solution
        problem_3 = OLBC_solver(model_3, 1, x0.flatten(), config)
        problem_3.problem.add_option('tol' , 10e-8)
        problem_3.problem.add_option('constr_viol_tol' , 10e-6)
        problem_3.problem.add_option('acceptable_tol' , 10e-6)
        problem_3.solve_and_save()
        problem_3.plot_res_type_1(0, '', 'fig')
        
        
    


# =============================================================================
# DEMO on the scenario with optimal gains
# =============================================================================

# TODO: find the optimal gains

if False:
    

    scenario_name = 'scenario_I'

        
    config = {
              'K_angles' : 10*2*8*2,
              'K_angles_rates' : 10*2*8*10,
              'K_effort' : 0.001/6,
              'K_regu' : 0.05,
              'K_speed' : 200*300,
              
              'roll_control' : False,
              'steer_torque' : True,
              'N_sampling' : 4,
              'filtering' : {'use_filtering' : False,
                             'low_cut_freq' : 0.01,
                             'high_cut_freq' : 5},
              'synthetic' : True,
              'ti':0,
              'tf':30
              }
    

    run_in_2_folds(scenario_name, config)
    
if True:
    
    
    path_res = 'D:/Users/ronne/Documents/4_side_quest/OpenLoopBalanceControl/results/'
    
    result_file = '2026_10_12_19_17_44_part_1_trial_20261012_105653'
    
    
    res = pd.read_pickle(path_res + result_file + '/' + result_file + '.pkl')
    
    NUM_NODES = len(res['time_simu'])
    sol = res['solution'].reshape(-1, NUM_NODES).T
    
    # TODO: mieux exporter le nom des variables
    columns = ['q1','q2','q3','q4','q5','q6','q7','q8'] + ['u1','u2','u3','u4','u5','u6','u7','u8'] + ['T6', 'T7']
    
    data_opt = pd.DataFrame(data=sol, columns=columns)
    run = '20261012_105653'
    data_exp = pd.read_csv(path_scenario + f'{run}/' + 'states_and_torques.csv')
    
    stats = []
    
    RMSE_q3 = RMSE(data_opt['q3'], data_exp['yaw angle'])
    RMSE_q4 = RMSE(data_opt['q4'], data_exp['roll angle'])
    RMSE_q7 = RMSE(data_opt['q7'], data_exp['steer angle'])
    RMSE_u3 = RMSE(data_opt['u3'], data_exp['yaw rate'])
    RMSE_u4 = RMSE(data_opt['u4'], data_exp['roll rate'])
    RMSE_u7 = RMSE(data_opt['u7'], data_exp['steer rate'])
    RMSE_T6 = RMSE(data_opt['T6'], data_exp['pedal torque T6'])
    RMSE_T7 = RMSE(data_opt['T7'], data_exp['steer torque T7'])
    
        
    ax, diff_mean, diff_std = plot_BA(data_opt, data_exp, 'T6', 'pedal torque T6',
            'Mean [Nm]', '$T6_{opt} - T6_{synth}$ [Nm]')
    plt.savefig(path_scenario + f'BA_T6_{result_file}.svg')
    
    ax, diff_mean, diff_std = plot_BA(data_opt, data_exp, 'T7', 'steer torque T7',
            'Mean [Nm]', '$T7_{opt} - T7_{synth}$ [Nm]')
    plt.savefig(path_scenario + f'BA_T7_{result_file}.svg')
    
