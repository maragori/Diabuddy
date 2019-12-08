# STRUCTURE: TASK METHOD
import numpy as np
from HELPER import Message

class Task:
    '''
    control structure, only this class calls method in the main() function
    '''

    def __init__(self, monitor, assess, diagnose, base, predictions):
        '''
        init class values, receives 4 objects of class Monitor, Assess, Diagnose and Base
        '''
        self.monitor = monitor
        self.assess = assess
        self.diagnose = diagnose
        self.base = base
        self.predictions = predictions

    def monitor_control(self, current_BGC, nutrition, exercise, insulin):
        '''
        starts the monitoring loop of the inference structure, calls the inference steps:
        1) receive
        2) select
        3) predict
        4) compare

        in:  float current BGC, 5 tuple nutrition, 3 tuple exercise, float insulin
        out: float diffscore, float future BGC
        '''

        print(f'Starting monitoring sequence with current blood glucose concentration {np.round(current_BGC,2)}.')
        observation = self.monitor.receive(current_BGC, nutrition, exercise, insulin)
        parameters = self.monitor.select(observation)
        predicted = self.monitor.predict(parameters, self.base, self.predictions)
        diffscore = self.monitor.compare(predicted, self.base)

        return diffscore, predicted

    def assess_control(self, diffscore):
        '''
        starts the assessment step of the inference structure, calls the following inference steps:
        1) specify
        2) select
        3) evaluate
        4) match

        in: float diffscore
        out: bool decision
        '''

        print(f'Starting assessment sequence with diffscore {np.round(diffscore,2)}.')

        diffscore, norms = self.assess.specify(diffscore, self.base)
        norm, normtype = self.assess.select(diffscore, norms, self.base)
        norm_val, normtype = self.assess.evaluate(diffscore, norm, normtype)
        decision = self.assess.match(norm_val, normtype)

        return decision

    def diagnose_control(self, current_BGC, nutrition, exercise, insulin, decision, predicted):
        '''
        starts the diagnose step of the inference structure, calls the following inference steps:
        1) cover
        2) select
        3) specify
        4) obtain
        5) verify

        in: current BGC, nutrition, exercise, insulin, decision
        out: list of results
        '''
        print(f'Starting diagnose sequence with current blood glucose concentration {np.round(current_BGC,2)},')
        print(f'future blood glucose concentration {np.round(predicted,2)}, and intervention = {decision}')

        hypotheses = self.diagnose.cover(decision, self.base)
        print('hypotheses', hypotheses)
        results = {}
        while hypotheses:
            hypothesis, hypotheses = self.diagnose.select(hypotheses)
            observable = self.diagnose.specify(hypothesis, self.base)
            finding = self.diagnose.obtain(observable, current_BGC, nutrition, exercise, insulin)
            result = self.diagnose.verify(finding, hypothesis, self.base)
            results[hypothesis] = result

        # CALCULATE AMOUNT INSULIN NEEDED/AMOUNT GLUCOSE
        if decision[1] == 'upper':
            correction = self.base.calculate_correction_ins(self.predictions)

        elif decision[1] == 'lower':
            correction = self.base.calculate_correction_sugar(self.predictions)

        message = Message(results, decision, correction)

        return results, message
