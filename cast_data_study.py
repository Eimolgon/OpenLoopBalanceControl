# -*- coding: utf-8 -*-
"""
Created on Mon Oct 12 19:00:37 2026

@author: ronne
"""
import numpy as np
from OLBC_main import OLBC_solver, OLBC_model
from scipy.interpolate import CubicSpline
import pandas as pd
from utils import NRMSE_and_RMSE, plot_BA, apply_lag, butter_lowpass_filter
import seaborn as sns
import matplotlib.pyplot as plt
from scipy import signal



path_scenario = 'D:/Users/ronne/Documents/4_side_quest/OpenLoopBalanceControl/data/cast_experiment/csv/'


# =============================================================================
# Functions
# =============================================================================

def run_in_2_folds(scenario_name, config):
    
    ## Define a fisrt model with full steering and litte points
    
    model_1 = OLBC_model(path_scenario, scenario_name, config)
    
    model_1.initialize_model(config['bike'])
    
    problem_1 = OLBC_solver(model_1, config=config)
    
    problem_1.solve_and_save()
    


    previous_solution = problem_1.solution.reshape(model_1.x0_shape)
    # problem_1.plot_res_type_1(0, '', 'fig')
    
    ## Define a second model with more points
    if True:
        config['N_sampling'] = 2
        model_2 = OLBC_model(path_scenario, scenario_name, config)
        model_2.initialize_model(config['bike'])
        
        x0 = np.zeros(model_2.x0_shape)
        
        for i in range(previous_solution.shape[0]):
            x0_i_interpolated = CubicSpline(model_1.x_meas_dict['time'], previous_solution[i, :])
            x0[i, :] = x0_i_interpolated(model_2.x_meas_dict['time'])
        
        problem_2 = OLBC_solver(model_2, x0.flatten(), config = config)
        path_to_results = problem_2.solve_and_save()
        previous_solution = problem_2.solution.reshape(model_2.x0_shape)
        problem_2.plot_res_type_1(1, '', 'fig')
    
    # ## Define a new model that include roll control as well
    # if False:
    #     config['roll_control'] = True
    #     model_3 = OLBC_model(path_scenario, scenario_name, config)
    #     model_3.initialize_model(config['bike'])
    #     # model_3.eoms= model_3.eoms*10
            
    #     x0 = np.zeros(model_3.x0_shape)
    #     x0[:previous_solution.shape[0], :] = previous_solution
    #     problem_3 = OLBC_solver(model_3, 1, x0.flatten(), config)
    #     problem_3.problem.add_option('tol' , 10e-8)
    #     problem_3.problem.add_option('constr_viol_tol' , 10e-6)
    #     problem_3.problem.add_option('acceptable_tol' , 10e-6)
    #     problem_3.solve_and_save()
    #     problem_3.plot_res_type_1(0, '', 'fig')
        
    return(path_to_results, problem_1)



# =============================================================================
# DEMO on the scenario with optimal gains
# =============================================================================

# TODO: find the optimal gains

if False:

    scenario_name = '00190'
    df = pd.read_csv(path_scenario + scenario_name + '.csv', sep=';')
    sns.relplot(df, x='time', y='seat force Fy')
    sns.displot(df, x='steer torque T7')
    
    list_df = []
    
    
    
    for run in ['00184','00185','00186','00190','00191','00192','00248','00249','00250','00251','00252','00253','00255','00256','00257']:
        df = pd.read_csv(path_scenario + str(run) + '.csv', sep=';')
        list_df.append(df)
        
        u7d = np.gradient(df['steer rate'], df['time'])
        T7 = df['steer torque T7']
        
        u7d_std = np.std(u7d)
        
        lag_samples = int(round(-0.073 * 200))
        T7 = apply_lag(T7, lag_samples)
        T7_std = np.std(T7)

        correlation = signal.correlate(u7d/u7d_std, T7/T7_std, mode="full")/min(len(u7d),len(T7))
        R2_max = np.max(correlation)**2
        lags = signal.correlation_lags(u7d.size, T7.size, mode="full")
        fs = 200
        lag = lags[np.argmax(correlation)]/fs
        print(lag)
        
    df_agregated = pd.concat(list_df)
    sns.displot(df_agregated, x='steer torque T7')
    
    print(len(df_agregated['steer torque T7']))
    print(df_agregated['steer torque T7'].mean())
    print(df_agregated['steer torque T7'].mean()/(df_agregated['steer torque T7'].std()))
    
    # u7d = np.gradient(df['steer rate'], df['time'])
    # T7 = df['steer torque T7']
    
    # u7d_std = np.std(u7d)
    # T7_std = np.std(T7)


    
    # correlation = signal.correlate(u7d/u7d_std, T7/T7_std, mode="full")/min(len(u7d),len(T7))
    # R2_max = np.max(correlation)**2
    # lags = signal.correlation_lags(u7d.size, T7.size, mode="full")
    # fs = 200
    # lag = lags[np.argmax(correlation)]/fs
    # print(lag)


    
if True:
    
    list_runs = ['00184','00185','00186','00190','00191','00192','00248','00249','00250','00251','00252','00253','00255','00256','00257']
    list_runs = ['00184', '00185','00186','00190']
    
    cutting_times = [[(0,4), (5,10), (11.5, 16), (18, 24), (25.5, 30.5), (32, 37), (39, 43), (45, 50), (52, 57)],
                        [(0,6), (13,24), (28, 32), (18, 24), (35, 44), (47, 53), (55, 59)],
                        [(0,7), (16,24), (27, 32), (35,45), (49,54)],
                        [(0,7), (16,21), (30,36), (38,42), (45,50), (52,60)]]
    
    list_df_for_stats = []
    
    for k, run in enumerate(list_runs):
        
        scenario_name = run
        
        for i, trial in enumerate(cutting_times[k]):
            
            (ti, tf) = cutting_times[k][i]


        # for ti,tf in cutting_times:
            
            config = {
                      'K_angles' : 10*2*8*40,
                      'K_angles_rates' : 10*2*8*10,
                      'K_efforts' : 0.001,
                      'K_regu' : 0.001,
                      'K_speed' : 1000,
                      
                      'roll_control' : False,
                      'steer_torque' : True,
                      'N_sampling' : 10,
                      'filtering' : {'use_filtering' : True,
                                     'low_cut_freq' : 0.01,
                                     'high_cut_freq' : 5,
                                     'offset_T7' : -0.31,
                                     'lag_T7': -0.072},
                      
                      'validation_data' : 'CAST',
                      'ti':ti,
                      'tf':tf,
                      'bike' : 'CastBike',
                      'F_y' : False,
                     
                      }
    
    
            path_to_results, problem_1 = run_in_2_folds(scenario_name, config)
    
            if True:
                
                
                path_res = 'D:/Users/ronne/Documents/4_side_quest/OpenLoopBalanceControl/'
                
                result_file = path_to_results
                
                
                res = pd.read_pickle(path_res + result_file)
                
                NUM_NODES = len(res['time_simu'])
                sol = res['solution'].reshape(-1, NUM_NODES).T
                
                # TODO: mieux exporter le nom des variables
                columns = ['q1','q2','q3','q4','q5','q6','q7','q8'] + ['u1','u2','u3','u4','u5','u6','u7','u8'] + ['T6', 'T7']
                
                data_opt = pd.DataFrame(data=sol, columns=columns)
                # run = '20261012_105653'
                data_exp = pd.read_csv(path_scenario + '/' + f'{scenario_name}.csv', sep=';')
                
                if config['filtering']['use_filtering']==True:
                    
                    T7_exp = data_exp['steer torque T7']
                    highcut = config['filtering']['high_cut_freq']
                    fs = 200

                    T7_exp = butter_lowpass_filter(T7_exp, highcut, fs, order=4)

                    if config['filtering']['offset_T7'] is not None:
                        
                        T7_exp = T7_exp - config['filtering']['offset_T7']
                                    
                    if config['filtering']['lag_T7'] is not None:

                        lag_samples = int(round((config['filtering']['lag_T7'] + 0.04)*200))
                        T7_exp = apply_lag(T7_exp, lag_samples)
                
                    data_exp['steer torque T7'] = T7_exp
                    
                
                
                stats = []
                
                RMSE_q3, NRMSE_q3, _, _ = NRMSE_and_RMSE(data_opt, data_exp, 'q3', 'yaw angle', ti, tf, config['N_sampling'])
                RMSE_q4, NRMSE_q4, _, _ = NRMSE_and_RMSE(data_opt, data_exp, 'q4', 'roll angle', ti, tf, config['N_sampling'])
                RMSE_q7, NRMSE_q7, _, _ = NRMSE_and_RMSE(data_opt, data_exp, 'q7', 'steer angle', ti, tf, config['N_sampling'])
                RMSE_u3, NRMSE_u3, _, _ = NRMSE_and_RMSE(data_opt, data_exp,  'u3', 'yaw rate', ti, tf, config['N_sampling'])
                RMSE_u4, NRMSE_u4, _, _ = NRMSE_and_RMSE(data_opt, data_exp, 'u4', 'roll rate', ti, tf, config['N_sampling'])
                RMSE_u7, NRMSE_u7, _, _ = NRMSE_and_RMSE(data_opt, data_exp, 'u7', 'steer rate', ti, tf, config['N_sampling'])
                # RMSE_T6 = RMSE(data_opt['T6'], data_exp['pedal torque T6'])
                RMSE_T7, NRMSE_T7, R2_T7, lag_T7 = NRMSE_and_RMSE(data_opt, data_exp, 'T7', 'steer torque T7', ti, tf, config['N_sampling'])
                

                
                
                # T7_error = data_opt['T7'] - data_exp['steer torque T7']
                
                # plt.plot(data_exp['steer rate'], T7_error)
                
                    
                # ax, diff_mean_T6, diff_std_T6 = plot_BA(data_opt, data_exp, 'T6', 'pedal torque T6',
                #         'Mean [Nm]', '$T6_{opt} - T6_{synth}$ [Nm]')
                # plt.savefig(path_scenario + f'BA_T6_{result_file}.svg')
                
                ax, diff_mean_T7, diff_std_T7 = plot_BA(data_opt, data_exp, 'T7', 'steer torque T7',
                        'Mean [Nm]', '$T7_{opt} - T7_{exp}$ [Nm]')
                plt.savefig(path_res+result_file[:-len(result_file.split('/')[-1])] + f'BA_T7.svg')
                plt.savefig(path_res+result_file[:-len(result_file.split('/')[-1])] + f'BA_T7.png')
            
                
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
                df_stats.to_csv(path_res+result_file[:-len(result_file.split('/')[-1])] + f'stats.csv')
                
                list_df_for_stats.append(df_stats)




new_list_df = []
cols = ['ti', 'tf',
'diff_mean_T7', 'diff_std_T7', 'RMSE_q3', 'RMSE_q4', 'RMSE_q7',
'RMSE_u3', 'RMSE_u4', 'RMSE_u7', 'RMSE_T7', 'NRMSE_q3', 'NRMSE_q4',
'NRMSE_q7', 'NRMSE_u3', 'NRMSE_u4', 'NRMSE_u7', 'NRMSE_T7', 'R2_T7',
'lag_T7']

for df in list_df_for_stats:
    df = df.T
    df[cols] = df[cols].astype('float')
    new_list_df.append(df)

df_stats_Cast_exp = pd.concat(new_list_df)
df_stats_Cast_exp.to_csv('D:/Users/ronne/Documents/4_side_quest/OpenLoopBalanceControl/results/df_stats_Cast_exp.csv')


for col in cols[2:]:
    
    print(col, '-', df_stats_Cast_exp[col].mean(),'(',
    df_stats_Cast_exp[col].std(),')')

    


