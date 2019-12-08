# HELPER CLASSES

import numpy as np


class Message:
    '''
    class that stores intervention message content
    '''

    def __init__(self, results, decision, correction):
        self.results = results
        self.decision = decision
        self.correction = correction

    def __str__(self):

        message_string = '\n\n###### INTERVENTION MESSAGE ######\n\n'
        # message if blood glucose will be too low
        if self.decision[1] == 'lower':

            # check hypotheses

            message_string += 'I detected that your blood sugar will be too low within the next 60 minutes. \nIt seems like this is due to the following actions you took: \n\n'

            if self.results['insulin']:
                message_string += 'You injected fast insulin recently \n\n'
            if self.results['moderate_exercise']:
                message_string += 'You are currently exercising at moderate intensity\n'

            message_string += f'I would advise you to eat {np.round(self.correction)} grams of sugar in order to keep your \nglucose levels in the goal range.'

        # message if blood glucose will be too high
        if self.decision[1] == 'upper':

            # check hypotheses

            message_string += 'I detected that your blood sugar will be too high within the next 60 minutes. \nIt seems like this is due to the following actions you took: \n\n'

            if self.results['food']:
                message_string += 'You ate a carbohydrate rich meal recently \n\n'
            if self.results['intense_exercise']:
                message_string += 'You are currently exercising at high intensity\n'

            message_string += f'I would advise you to inject {np.round(self.correction)} units of fast insulin in order to keep your \nglucose levels in the goal range.'

        if not message_string:
            print('Warning. Message could not be generated. Unknown decision category.')

        return message_string


class Predictions:

    def __init__(self):
        self.master_list = 144 * [100.]  # list of values, corresponding to 24h period in timesteps of 10 min
        self.influences = []  # list of lists of influences

