# OpenLoopBalanceControl
Code and Data to perform trajectories optimization from bicycle (+rider) motion and get the control troques of the rider.

## Context and Objectives
- The torque based cyclist balance strategy is poorly describe in the litrature, need for observation, quantification and description
- The link between cyclist control actions and workload is still unknown, gaze based workload metrics and balance performance metrics can be used as workload proxy

## Aim of this code
This code is meant to be a open tool to estimate cyclist's control torques from bicycle motion.
Sources of motion can be diverse (mocap, IMU, GPS etc.).
Complexity of the model can be adjusted : rigid rider, leaning rider, more advanced...

## Analysis to do
- impact of model complexity on tracking performance and accuracy (real data + synthetic data)
- What is a/the good/best performance metric for this method?
- sensitivity analysis to bicycle and rider parameters
- IMU to torques ? What's the best setting ? 
- compare torque control metrics to gaze metrics

## TO DO
- make a rigid rider model -> Done
- generate synthetic data with a leaning rider, ie: we know the torques and the motion and we test our method
- run the method on real data :
- hands-off cycling, do we get a very low steer torque? -> We get full steer torque, most controllabe input
- data with steer torque sensor, compute accuracy
- data with chest cast, do we get a very low roll torque?
- find correlations between accuracy and tracking performance
- run Morris analysis with bicycle parameters

## Installation and Usage

Clone the repository where the development is done:

```
git clone git@github.com:jrPhD/OpenLoopBalanceControl
```

Install [miniforge](https://conda-forge.org/miniforge/) (or miniconda or
anaconda). Open the command prompt (conda prompt on windows) and type:

You will also need a working C compiler on your operating system. For Windows,
you'll need the right compiler for the Python version you are using. See
https://wiki.python.org/moin/WindowsCompilers for more info.

If using Spyder, install it along with ``spyder-kernels`` in your base
environment::

```
conda install spyder spyder-kernels
```

Install the conda environment for the gait closed loop id project:

```
cd OpenLoopBalanceControl
conda env create -f openloopbalancecontrol-env.yml
conda activate openloopbalancecontrol
```

If we make updates in pydy or opty (because we are using the development
versions), you will need to either update the environment:

```
conda deactivate
conda env update -f openloopbalancecontrol-env.yml
conda activate openloopbalancecontrol
```

or recreate the environment:

```
conda deactivate
conda env remove -n openloopbalancecontrol
conda env create -f openloopbalancecontrol-env.yml
conda activate openloopbalancecontrol
```

## How to use the code ?

### Basics 
- the main functions and class are in the ```OLBC_main.py``` file.
- you must have a csv file with your experimental measurments in folder located in root/data/your_folder
- columns of the csv file must be the state variables of that bicycle across time, each line is a timestamp 
- Use q1,q2,q3,...,q8,u1,...,u8 as columns names following Moore PhD dissertation model
- You can add "speed" as a column for the bicycle speed
- q4 and q7 are mandatory, add also u4 and u7 if you have them
- Add a time vector as 'time' in a column
- you need bicycle parameters in the root/data/bicycles/my_bike folder using BicycleParamaters library
  
### Make a config dict

```
config = {
'K_angles' : 10*2*8*40, #Good value
'K_angles_rates' : 10*2*8*10,  #Good value
'K_efforts' : 0.001,  #Good value
'K_regu' : 0.001,   #Good value
'K_speed' : 1000,  #Good value
                      
'roll_control' : False, #Experimental, not recommanded so far
'steer_torque' : True, #Use steer control to control the bike
'N_sampling' : 1,
'filtering' : {'use_filtering' : True, #You can filter your data with a low pass filter
                 'low_cut_freq' : 0.01, #Not use so far
                 'high_cut_freq' : 5, #Tune this one if needed
                 'offset_T7' : 0, #Only needed if you have a reference measurement you use to validate the model and not used in the fitting process 
                 'lag_T7': 0}, #Only needed if you have a reference measurement you use to validate the model and not used in the fitting process 
                'validation_data' : 'synthetic', # Recommanded so far 
                'ti':ti, # You can select the initial time
                'tf':tf, # You can select the final time
                'bike' : 'Benchmark', # Name of the bicycle paramaters you use in the BicyclePAramaters library
                'F_y' : False, # Recommanded so far 
                      }
  ```

                        model_1 = OLBC_model(path_scenario, scenario_name, config)
    
    model_1.initialize_model(config['bike'])
    
    problem_1 = OLBC_solver(model_1, config=config)
    
    problem_1.solve_and_save()



