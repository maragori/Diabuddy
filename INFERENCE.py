# STRUCTURE: INFERENCE METHODS
import numpy as np
import matplotlib.pyplot as plt

# initialize data formats and values for demo
# all observations are stored 4-tuples with indices:

BGC = 0
NUT = 1
EX = 2
INS = 3

# all foods are stored in lists of length 5 with indices:

SUG = 0
FCARB = 1
SCARB = 2
FAT = 3
PROT = 4

# all exercise dataponts are stored in 3-tuples with indices:

STEP = 0
HR = 1
MET = 2


class Monitor:
    '''
    inference layer class mainly responsible for predicting future BGC and comparing to norm
    '''

    def __init__(self, demo):
        self.demo = demo

    def receive(self, current_BGC, nutrition, exercise, insulin):
        '''
        receive all data from smartphone application, i.e. current BGC, nutrition data, exercise data and insulin data

        in: BGC, nutrition, exercise, insulin data
        out: parsed data
        '''

        if not self.demo:
            print('Receive datapoints...', end='')

        # return all datapoints in 4 observation tuple
        observation = (current_BGC, nutrition, exercise, insulin)

        if not self.demo:
            print(' Done')

        return observation

    def select(self, observation):
        '''
        selects relevant parameters used in prediction step

        in: parsed data from receive step
        out: selected params for predict step
        '''

        if not self.demo:
            print('Select relevant parameters...', end='')

        # this will depend on the prediction model we use
        # probably use all parameters
        parameters = observation

        if not self.demo:
            print(' Done')
        return parameters

    def predict(self, parameters, base, predictions):
        '''
        predict future BGC +60 mins based on given params

        in: params from select step, knowledge base, prediction object
        out: predicted BGC
        '''

        print('Predicting future blood glucose concentration +60 min...', end='')
        # prediction of BGC based on the parameters and knowledge rules
        # model not finished
        # for now just increase BGC by 100
        '''
        gets predictions object with list of all n prediction timesteps <<< this ist MASTER list
        STEPS:
    
        1. move one timestep forward (remove first element, add one element at tail)
        2. update list according to new datapoint current_BGC (add/subtract difference of first element with current BGC to all list elements)
        3. apply all rules according to input params > get one list per param: add to influence list of lists in prediction object
        4. apply all influences on master list
        6. clear influence list
        7. return 6th entry of master list 
        '''

        # update the list: remove first element, append last element
        predictions.master_list = predictions.master_list[1:]
        predictions.master_list.append(predictions.master_list[-1])
        array_pred = np.array(predictions.master_list)

        # retrive subcut BGC from parameters, calculate prediction error, correct error
        bgc = parameters[BGC]
        prd_error = bgc - predictions.master_list[0]
        array_pred += prd_error

        # check which events need rules
        nutrition = parameters[NUT]
        exercise = parameters[EX]
        insulin = parameters[INS]

        ###### nutrition
        # generate influence lists
        if any(nutrition):

            fat_infl = base.fat_rule(nutrition[FAT])
            prot_infl = base.protein_rule(nutrition[PROT])
            delay = fat_infl + prot_infl

            if nutrition[SUG]:
                sugar_infl = base.sugar_rule(nutrition[SUG])
                sugar_infl = delay + sugar_infl
                predictions.influences.append(sugar_infl)

            if nutrition[FCARB]:
                fcarb_infl = base.fast_carb_rule(nutrition[FCARB])
                fcarb_infl = delay + fcarb_infl
                predictions.influences.append(fcarb_infl)

            if nutrition[SCARB]:
                scarb_infl = base.slow_carb_rule(nutrition[SCARB])
                scarb_infl = delay + scarb_infl
                predictions.influences.append(scarb_infl)

        ###### exercise
        steps = exercise[STEP]
        hr = exercise[HR]
        mets = exercise[MET]

        if 20 < steps < 120 and 90 < hr < 120 and 3 < mets < 6:
            ex_infl = base.moderate_exercise_rule()
            predictions.influences.append(ex_infl)

        elif steps > 120 and hr > 120 and mets > 6:
            ex_infl = base.intense_exercise_rule()
            predictions.influences.append(ex_infl)

        ##### insulin
        if insulin:
            ins_infl = base.insulin_rule(insulin)
            predictions.influences.append(ins_infl)


        # collapse everything into master list
        for influence in predictions.influences:

            influence_array = np.array(influence)
            influence_array.resize(array_pred.shape)
            array_pred = array_pred + influence_array

        predictions.master_list = list(array_pred)

        self.plot_predictions(predictions, 36)
        # select predicted BGC + 60 mins
        predicted = predictions.master_list[6]


        # discard all influences of the current timestep
        predictions.influences = []

        print(' Done')
        print(f'BGC +60 min will be {np.round(predicted,2)}')
        print('Full prediction timeline for the next 90 min:')
        print(np.round(array_pred[:9],2))
        return predicted

    def compare(self, predicted, base):
        '''
        compare predicted BGC to norm

        in: predicted BGC, base
        out: diffscore
        '''


        print(f'Comparing predicted to optimal...', end='')

        optimal = base.OPTIMAL_BGC
        diffscore = predicted - optimal

        print(' Done')
        print(f'Diffscore: {np.round(diffscore,2)}')
        return diffscore

    def plot_predictions(self, predictions, timesteps):
        """
        given a predictions object, plots current BGC predictions incl all influences on BGC at that timestep

        in: predictions object
        out: None
        """
        plt.style.use('ggplot')

        x = np.linspace(0,timesteps, timesteps)

        fig, (ax1, ax2) = plt.subplots(2,1,sharex=True)


        ax1.plot(x, np.array(predictions.master_list)[:timesteps], label='predicted glucose')

        for idx, influence in enumerate(predictions.influences):
            ax2.plot(x, np.array(influence)[:timesteps], label=f'influence_{idx+1}')


        ax1.legend()
        if predictions.influences:
            ax2.legend()
        ax2.set_xlabel('Timesteps (each timestep is 10 minutes)')
        plt.show()

class Assess:
    '''
    inference layer class used to evaluate whether BGC will behave abnormally
    '''

    def __init__(self, demo):
        self.demo = demo

    def specify(self, diffscore, base):
        '''
        specifies the norms that future BGC has to conform to in order to be classified as behaving normally

        in: diffscore
        out: list of norms
        '''

        if not self.demo:
            print(f'Specifying the norms..., ', end='')

        upper_limit = base.UPPER
        lower_limit = base.LOWER
        norms = [lower_limit, upper_limit]

        if not self.demo:
            print(' Done')

        return diffscore, norms

    def select(self, diffscore, norms, base):
        '''
        from the list of norms select the correct norm for the case

        in: case, list of norms, base
        out: norm
        '''

        # if predicted is higher than optimal, select upper norm
        # else select lower norm

        if not self.demo:
            print('Selecting relevant norm for the case...', end='')

        if diffscore >= 0:
            norm = norms[1]
            normtype = 'upper'
        else:
            norm = norms[0]
            normtype = 'lower'

        if not self.demo:
            print(' Done')
        print(f'Selected {normtype} norm {norm}')

        return norm, normtype

    def evaluate(self, diffscore, norm, normtype):
        '''
        calculate the norm value for the given diffscore and norm

        in: diffscore, norm
        out: norm value
        '''

        if not self.demo:
            print(f'Evaluating diffscore against {normtype} norm...', end='')

        # if norm_val positive: value outside norm
        if normtype == 'upper':
            norm_val = diffscore - norm
        elif normtype == 'lower':
            norm_val = norm - diffscore
        else:
            print('Invalid normtype specified.')

        if not self.demo:
            print(' Done')
        return norm_val, normtype

    def match(self, norm_val, normtype):
        '''
        use causal model to generate decision whether behavior will be abormal given the norm

        in: norm value
        out: decision
        '''

        if not self.demo:
            print('Matching norm value to decision category...', end='')

        decision = (True, normtype) if norm_val > 0 else (False, normtype)

        if not self.demo:
            print(' Done')

        if decision[0] and normtype == 'upper':
            print(f'An intervention should be sent because blood glucose will be too high')
        elif decision[0] and normtype == 'lower':
            print('An intervention should be sent because blood glucose will be too low')
        elif not decision[0]:
            print('Blood glucose will be in the acceptable range. No intervention needed')
        else:
            print('Unknown decision category.')

        return decision


class Diagnose:
    '''
    inference layer class responsible for diagnosing why behavior will be abnormal in the future
    '''

    def __init__(self, demo):
        self.demo = demo

    def cover(self, decision, base):
        '''
        for given decision, generate all possible hypotheses

        in: decision
        out: list of hypotheses
        '''

        if decision[0]:
            if not self.demo:
                print('Generating set of possible hypotheses...', end='')

            if decision[1] == 'upper':

                hypotheses = base.too_high()
                if not self.demo:
                    print(' Done')
                return hypotheses

            elif decision[1] == 'lower':
                hypotheses = base.too_low()
                if not self.demo:
                    print(' Done')
                return hypotheses

            else:
                print('Could not generate hypotheses set. Unknown decision category.')
                return None

        elif not decision[0]:
            print('Error. In Diagnose step while no intervention needed.')
            return None



    def select(self, hypotheses):
        '''
        select a single hypotheses to test

        in: list of hypotheses
        out: hypothesis
        '''

        # every time this function is called, it returns and removes the last hypothesis from stack

        return hypotheses.pop(), hypotheses

    def specify(self, hypothesis, base):
        ''' given hypothesis, specify what data has to be checked

        in: hypothesis, base
        out: observable to be checked
        '''

        if not self.demo:
            print(f'Specifying the observables for hypothesis {hypothesis}...', end='')

        observable = base.causal_model(hypothesis)

        if not self.demo:
            print(' Done')
        return observable

    def obtain(self, observable, nutrition, exercise, insulin):
        '''
        obtain the current values for the specified observable

        in: observable, macronutritions, exercise, insulin
        out: finding
        '''

        if not self.demo:
            print(f'Obtaining observable {observable}...', end='')

        if observable == 'nutrition':
            if not self.demo:
                print(' Done')
            return nutrition

        elif observable == 'insulin':
            if not self.demo:
                print(' Done')
            return insulin

        elif observable == 'exercise':
            if not self.demo:
                print(' Done')
            return exercise

        else:
            print('Error obtaining observables')

    def verify(self, finding, hypothesis, base):
        '''
        given findings and hypothesis, verify whether hypothesis is true

        in: finding, hypothesis, base
        out: result
        '''

        if not self.demo:
            print(f'Verifying hypothesis {hypothesis}...', end='')

        result = base.check_hypothesis(hypothesis, finding)

        if not self.demo:
            print(' Done')
        return result


