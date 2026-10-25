# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 19:00:37 2026

@author: ronne
"""
import numpy as np
from OLBC_main import OLBC_solver, OLBC_model
from scipy.interpolate import CubicSpline
import pandas as pd
from utils import NRMSE_and_RMSE, plot_BA
# import seaborn as sns
import matplotlib.pyplot as plt



path_scenario = 'D:/Users/ronne/Documents/4_side_quest/OpenLoopBalanceControl/data/synthetic/'


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


def compute_RMSE(path_to_results, scenario_name):
    
    path_res = 'D:/Users/ronne/Documents/4_side_quest/OpenLoopBalanceControl/'
    
    result_file = path_to_results
    
    
    res = pd.read_pickle(path_res + result_file)
    
    NUM_NODES = len(res['time_simu'])
    sol = res['solution'].reshape(-1, NUM_NODES).T
    
    # TODO: mieux exporter le nom des variables
    columns = ['q1','q2','q3','q4','q5','q6','q7','q8'] + ['u1','u2','u3','u4','u5','u6','u7','u8'] + ['T6', 'T7']
    
    data_opt = pd.DataFrame(data=sol, columns=columns)
    run = scenario_name
    data_exp = pd.read_csv(path_scenario + f'{run}/' + 'states_and_torques.csv')
    
    stats = []
    
    RMSE_q4 = RMSE(data_opt['q4'], data_exp['roll angle'])
    RMSE_q7 = RMSE(data_opt['q7'], data_exp['steer angle'])
    RMSE_u4 = RMSE(data_opt['u4'], data_exp['roll rate'])
    RMSE_u7 = RMSE(data_opt['u7'], data_exp['steer rate'])
    RMSE_T6 = RMSE(data_opt['T6'], data_exp['pedal torque T6'])
    RMSE_T7 = RMSE(data_opt['T7'], data_exp['steer torque T7'])
    
    return(RMSE_q4, RMSE_q7, RMSE_u4, RMSE_u7, RMSE_T6, RMSE_T7)



def fun_SA():
    
    config = {
              'K_angles' : 10*2*8*20,
              'K_angles_rates' : 10*2*8*10,
              'K_efforts' : 0.001/6,
              'K_regu' : 15,
              'K_speed' : 200*300,
              
              'roll_control' : False,
              'steer_torque' : True,
              'N_sampling' : 10,
              'filtering' : {'use_filtering' : False,
                             'low_cut_freq' : 0.01,
                             'high_cut_freq' : 5},
              'validation_data' : 'synthetic',
              'ti' : 0,
              'tf' : 3,
              'bike' : 'Synth_bike_n',
              'F_y' : False
              }
    
    path_to_results = run_in_2_folds('scenario_I', config)
    res = compute_RMSE(path_to_results, 'scenario_I')
    
    return(res)



# scenario_name = '20261012_105653'

# fun_SA(scenario_name)

# =============================================================================
# DEMO on the scenario with optimal gains
# =============================================================================

# TODO: find the optimal gains

if True:
    

    scenario_name = '20261012_105653'

        
    config = {
              'K_angles' : 10*2*8*20,
              'K_angles_rates' : 10*2*8*10,
              'K_efforts' : 0.001/6,
              'K_regu' : 15,
              'K_speed' : 200*300,
              
              'roll_control' : False,
              'steer_torque' : True,
              'N_sampling' : 4,
              'filtering' : {'use_filtering' : False,
                             'low_cut_freq' : 0.01,
                             'high_cut_freq' : 5},
              'validation_data' : 'synthetic',
              'ti': 0,
              'tf': 30,
              'bike': 'Browser',
              'F_y' : False
              }
    

    path_to_results = run_in_2_folds(scenario_name, config)
    
if False:
    
    
    path_res = 'D:/Users/ronne/Documents/4_side_quest/OpenLoopBalanceControl/results/'
    
    result_file = '2026_10_23_12_10_56_part_1_trial_20261012_105653'
    
    
    res = pd.read_pickle(path_res + result_file + '/' + result_file + '.pkl')
    
    NUM_NODES = len(res['time_simu'])
    sol = res['solution'].reshape(-1, NUM_NODES).T
    
    # TODO: mieux exporter le nom des variables
    columns = ['q1','q2','q3','q4','q5','q6','q7','q8'] + ['u1','u2','u3','u4','u5','u6','u7','u8'] + ['T6', 'T7']
    
    data_opt = pd.DataFrame(data=sol, columns=columns)
    run = '20261012_105653'
    data_exp = pd.read_csv(path_scenario + f'{run}/' + 'states_and_torques.csv')
    
    stats = []
    
    ti , tf = config['ti'], config['tf']
    
    config['N_sampling'] = 1
    
                
    RMSE_q3, NRMSE_q3, _, _ = NRMSE_and_RMSE(data_opt, data_exp, 'q3', 'yaw angle', ti, tf, config['N_sampling'])
    RMSE_q4, NRMSE_q4, _, _ = NRMSE_and_RMSE(data_opt, data_exp, 'q4', 'roll angle', ti, tf, config['N_sampling'])
    RMSE_q7, NRMSE_q7, _, _ = NRMSE_and_RMSE(data_opt, data_exp, 'q7', 'steer angle', ti, tf, config['N_sampling'])
    RMSE_u3, NRMSE_u3, _, _ = NRMSE_and_RMSE(data_opt, data_exp,  'u3', 'yaw rate', ti, tf, config['N_sampling'])
    RMSE_u4, NRMSE_u4, _, _ = NRMSE_and_RMSE(data_opt, data_exp, 'u4', 'roll rate', ti, tf, config['N_sampling'])
    RMSE_u7, NRMSE_u7, _, _ = NRMSE_and_RMSE(data_opt, data_exp, 'u7', 'steer rate', ti, tf, config['N_sampling'])
    RMSE_T6, NRMSE_T6, R2_T6, lag_T6 = NRMSE_and_RMSE(data_opt, data_exp, 'T6', 'pedal torque T6', ti, tf, config['N_sampling'])
    RMSE_T7, NRMSE_T7, R2_T7, lag_T7 = NRMSE_and_RMSE(data_opt, data_exp, 'T7', 'steer torque T7', ti, tf, config['N_sampling'])
    

    
    
    # T7_error = data_opt['T7'] - data_exp['steer torque T7']
    
    # plt.plot(data_exp['steer rate'], T7_error)
    
        
    # ax, diff_mean_T6, diff_std_T6 = plot_BA(data_opt, data_exp, 'T6', 'pedal torque T6',
    #         'Mean [Nm]', '$T6_{opt} - T6_{synth}$ [Nm]')
    # plt.savefig(path_scenario + f'BA_T6_{result_file}.svg')
    
    ax, diff_mean_T7, diff_std_T7 = plot_BA(data_opt, data_exp, 'T7', 'steer torque T7',
            'Mean [Nm]', '$T7_{opt} - T7_{exp}$ [Nm]')
    plt.savefig(path_res+result_file[:-len(result_file.split('/')[-1])] + 'BA_T7.svg')
    plt.savefig(path_res+result_file[:-len(result_file.split('/')[-1])] + 'BA_T7.png')

    
    stats.append([result_file.split('/')[-1][:-4], 
                  res['config']['K_angles'],
                  res['config']['K_angles_rates'],
                  res['config']['K_efforts'],
                  res['config']['K_regu'],
                  res['config']['K_speed'],
                  res['config']['roll_control'],
                  res['config']['steer_torque'],
                  res['config']['validation_data'],
                  res['config']['ti'],
                  res['config']['tf'],
                  # diff_mean_T6,
                  # diff_std_T6,
                  diff_mean_T7,
                  diff_std_T7,
                  RMSE_q3,
                  RMSE_q4,
                  RMSE_q7,
                  RMSE_u3,
                  RMSE_u4,
                  RMSE_u7,
                  # RMSE_T6,
                  RMSE_T7,
                  NRMSE_q3,
                  NRMSE_q4,
                  NRMSE_q7,
                  NRMSE_u3,
                  NRMSE_u4,
                  NRMSE_u7,
                  NRMSE_T7,
                  R2_T7,
                  lag_T7])
    
    columns = ['run','K_angles','K_angles_rates','K_effort',
               'K_regu','K_speed','roll_control','steer_torque',
               'validation_data','ti','tf',
               # 'diff_mean_T6',
               # 'diff_std_T6',
               'diff_mean_T7',
               'diff_std_T7',
               'RMSE_q3',
               'RMSE_q4',
               'RMSE_q7',
               'RMSE_u3',
               'RMSE_u4',
               'RMSE_u7',
               # 'RMSE_T6',
               'RMSE_T7',
                  'NRMSE_q3',
                  'NRMSE_q4',
                  'NRMSE_q7',
                  'NRMSE_u3',
                  'NRMSE_u4',
                  'NRMSE_u7',
                  'NRMSE_T7',
                  'R2_T7',
                  'lag_T7']
    
    df_stats = pd.DataFrame(np.array(stats).T, columns)
    df_stats.to_csv(path_res+result_file[:-len(result_file.split('/')[-1])] + 'stats.csv')
