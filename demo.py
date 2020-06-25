#!/usr/bin/python3

# DEMO
import numpy as np
import argparse
from BASE import Base
from HELPER import Predictions, init_scenario
from INFERENCE import Monitor, Assess, Diagnose
from TASK_METHOD import Task

# initialize data formats and values for demo

# all observations are stored 4-tuples with indices:
BGC = 0
NUT = 1
EX = 2
INS = 3

# all foods are stored in 5-tuples with indices:
SUG = 0
FCARB = 1
SCARB = 2
PROT = 4
FAT = 3

# all exercise dataponts are stored in 3-tuples with indices:
STEP = 0
HR = 1
MET = 2

parser = argparse.ArgumentParser(
    description='Demo script for DiaBuddy'
)

parser.add_argument('-s', '--scenario', type=int, help="Choice of scenario. 1/2 are valid choices.", default=1)
parser.add_argument('-c', '--currentbgc', type=int, help="Starting BGC", default=100)
parser.add_argument('-d', '--demo', type=bool, help="Demo flag. If false, whole trace is printed.", default=True)

args = parser.parse_args()

# this bool is only to be set to 'True' for demo purposes: the system DOES NOT PRINT FULL TRACES when this is set as true
DEMO = args.demo

# CONFIGURATIONS FOR SCENARIOS: choose 1 or 2
SCENARIO = args.scenario


# initialize scenario configuration
nutritions, exercises = init_scenario(SCENARIO)

# starting blood glucose
current_BGC = args.currentbgc


print(f"Running scenario {SCENARIO}")
print(f"Starting blood glucose is set to {current_BGC}")
print(f"Running in {'demo' if DEMO else 'debug'} mode")

# starting insulin injection, each timestep with intervention new insulin can be inputted
i = 0
insulin_correction = False
s = 0
sugar_correction = False

# initialize objects for task, inference and domain
monitor = Monitor(DEMO)
assess = Assess(DEMO)
diagnose = Diagnose(DEMO)
base = Base(DEMO)
predictions = Predictions()
task = Task(monitor, assess, diagnose, base, predictions, DEMO)


if __name__ == '__main__':

    # monitor loop
    for nutrition, exercise in zip(nutritions, exercises):

        if not DEMO:
            print(f'\n\n\nStarting control loop with current BGC: {np.round(current_BGC,2)}')

        # if intervention has been set, insert the input values into the iteration config
        if all([v == 0 for v in nutrition]):
            nutrition[SUG] = s if sugar_correction else 0
        insulin = i if insulin_correction else 0


        # monitor
        diffscore, predicted = task.monitor_control(current_BGC, nutrition, exercise, insulin)

        # assess
        decision = task.assess_control(diffscore)

        # diagnose, only if intervention is necessary
        if decision[0]:
            results, message = task.diagnose_control(current_BGC, nutrition, exercise, insulin, decision, predicted)
            print(message)

            if decision[1] == 'upper':
                print('Do you want to inject insulin? Select an amount of units of fast insulin between 0 and 10:')
                i = float(input())
                insulin_correction = True
                sugar_correction = False

            elif decision[1] == 'lower':
                print('Do you want to eat some sugar? Select a number of grams you want to eat between 0 and 100:')
                s = float(input())
                insulin_correction = False
                sugar_correction = True
        else:
            insulin_correction = False
            sugar_correction = False

        # because we do not work with actual sensory data, pretend that the next actual blood glucose value is the predicted value
        current_BGC = predictions.master_list[1]



