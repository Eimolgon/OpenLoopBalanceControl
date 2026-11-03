
from pathlib import Path

from OLBC_main import OLBC_model, OLBC_solver


# --------------------------------------------------
# INPUT DATA
# --------------------------------------------------

DATA_DIR = Path("~/Documents/PhD-Project/03-data-output/gopro_test_1_1").expanduser()
CSV_NAME = "states_jf_gopro_test_1_1"

# The loader expects DATA_DIR + CSV_NAME + ".csv"
# and uses semicolon-separated CSV files.


# --------------------------------------------------
# OPTIMIZATION CONFIGURATION
# --------------------------------------------------

# config = {
#     "K_angles": 10 * 2 * 8 * 40,
#     "K_angles_rates": 10 * 2 * 8 * 10,
#     "K_efforts": 0.001,
#     "K_regu": 0.001,
#     "K_speed": 1000,

#     "roll_control": False,
#     "steer_torque": True,

#     "N_sampling": 2,

#     "filtering": {
#         "use_filtering": True,
#         "low_cut_freq": 0.01,
#         "high_cut_freq": 5,
#     },

#     "validation_data": "CAST",

#     "ti": 0.0,
#     "tf": 10.0,

#     "bike": "CastBike",
#     "F_y": False,
# }

# config = {'roll_control' : False,
#               'K_effort' : 0.001/3,
#               'steer_torque' : True,
#               'N_sampling' : 4,
#               'filtering' : {'use_filtering' : True,
#                              'low_cut_freq' : 0.01,
#                              'high_cut_freq' : 5},
#               'validation_data' : 'MOCAP',
#               'bike' : "Browser",
#               'ti':0,
#               'tf': 3,
#               'F_y' : False,
#               }

config = {
    'K_angles' : 10*2*8*40, #Good value
    'K_angles_rates' : 10*2*8*10,  #Good value
    'K_efforts' : 0.001,  #Good value
    'K_regu' : 0.001,   #Good value
    'K_speed' : 1000,  #Good value
                  
    'roll_control' : False, #Experimental, not recommanded so far
    'steer_torque' : True, #Use steer control to control the bike
    'N_sampling' : 1,
    'validation_data': 'CAST',
    'filtering' : {'use_filtering' : True, #You can filter your data with a low pass filter
                'low_cut_freq' : 0.01, #Not use so far
                'high_cut_freq' : 5,}, #Tune this one if needed
    'ti': 0.0, # You can select the initial time
    'tf': 10.0, # You can select the final time
    'bike' : 'Benchmark', # Name of the bicycle paramaters you use in the BicyclePAramaters library
    'Fy' : False, # Recommended so far 
    }


# --------------------------------------------------
# LOAD EXPERIMENTAL DATA
# --------------------------------------------------

model = OLBC_model(
    str(DATA_DIR) + "/",
    CSV_NAME,
    config
)

# Initialize bicycle model
model.initialize_model(config["bike"])

# Inspect loaded measurements
model.plot_measurments(
    save=0,
    path=".",
    figname="measurements"
)


# --------------------------------------------------
# RUN OPTIMIZATION
# --------------------------------------------------

problem = OLBC_solver(
    model,
    config=config
)

problem.solve_and_save()

# Plot optimization results
problem.plot_results()

print("Optimization completed!")
