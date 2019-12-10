# STRUCTURE: KNOWLEDGE BASE

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
FAT = 3
PROT = 4

# all exercise dataponts are stored in 3-tuples with indices:

STEP = 0
HR = 1
MET = 2


class Base:
    '''
    class containing domain knowledge (static/rule based)
    '''
    OPTIMAL_BGC = 100
    UPPER = 60
    LOWER = -30

    KF_FACTOR = 40
    BE_FACTOR = 1
    BE_EF = KF_FACTOR * BE_FACTOR
    G_BE_EXCHANGE_FACTOR = 10

    # Delay Factors
    SUGAR_DELAY = 1  # 10-minute entities (=10min)
    FCARB_DELAY = 2
    SCARB_DELAY = 3
    INS_DELAY = 1

    # Fat and Protein Influence
    FAT_INFLUENCE = 0.5
    PROTEIN_INFLUENCE = 0.1

    # Duration Factors
    SUGAR_DURATION = 6  # (=60 min)
    FCARB_DURATION = 12
    SCARB_DURATION = 24
    INS_DURATION = 18

    def __init__(self, demo):
        self.demo = demo

    '''
    all of the following rule types assume an ADDITIVE model
    '''



    def too_low(self):
        '''
        returns the hypothesis set for too low blood glucose

        in:
        out: list of hypothesis
        '''

        return ['insulin', 'moderate_exercise']

    def too_high(self):
        '''
        returns the hypothesis set for too high blood glucose

        in:
        out: list of hypothesis
        '''
        return ['food', 'intense_exercise']

    def calculate_number_of_BE(self, g):

        """
        given a number of carbohydrates, calculate the number of BEs

        in: g carbohydrates
        out: BEs
        """
        number_of_BE = g / self.G_BE_EXCHANGE_FACTOR

        return number_of_BE

    def calculate_step_size(self, number_of_BEs, effect_duration):

        """
        given an amount of BEs and an effect duration, calculate the increase/decrease per time step

        in: BEs, duration of the effect
        out: step size
        """

        step_size = (self.BE_EF * number_of_BEs) / effect_duration
        return step_size

    def sugar_rule(self, g):
        '''
        effect of X gram sugar on the BGC

        in: gram sugar
        out: incrase in BGC
        '''

        sugar_infl = self.SUGAR_DELAY * [0]

        effect_duration = self.SUGAR_DURATION - self.SUGAR_DELAY
        number_of_BEs = self.calculate_number_of_BE(g)
        sugar_step_size = self.calculate_step_size(number_of_BEs, effect_duration)

        for i in range(1, effect_duration + 1):
            sugar_infl.append(sugar_step_size * i)

        # fill up to length 144
        val = sugar_infl[-1]
        fill_list = [val] * (144 - len(sugar_infl))
        sugar_infl = sugar_infl + fill_list

        return sugar_infl

    def fast_carb_rule(self, g):
        '''
        effect of X gram fast carbs on the BGC

        in: gram carbs
        out: incrase in BGC
        '''

        fcarb_infl = self.FCARB_DELAY * [0]

        effect_duration = self.FCARB_DURATION - self.FCARB_DELAY
        number_of_BEs = self.calculate_number_of_BE(g)
        fcarb_step_size = self.calculate_step_size(number_of_BEs, effect_duration)

        for i in range(1, effect_duration + 1):
            fcarb_infl.append(fcarb_step_size * i)

        # fill up to length 144
        val = fcarb_infl[-1]
        fill_list = [val] * (144 - len(fcarb_infl))
        fcarb_infl = fcarb_infl + fill_list

        return fcarb_infl

    def slow_carb_rule(self, g):
        '''
        effect of X gram slow carbs on the BGC

        in: gram slow carbs
        out: incrase in BGC
        '''

        scarb_infl = self.SCARB_DELAY * [0]

        effect_duration = self.SCARB_DURATION - self.SCARB_DELAY
        number_of_BEs = self.calculate_number_of_BE(g)
        scarb_step_size = self.calculate_step_size(number_of_BEs, effect_duration)

        for i in range(1, effect_duration + 1):
            scarb_infl.append(scarb_step_size * i)

        # fill up to length 144
        val = scarb_infl[-1]
        fill_list = [val] * (144 - len(scarb_infl))
        scarb_infl = scarb_infl + fill_list

        return scarb_infl

    def fat_rule(self, g):
        '''
        effect of X gram fat on the BGC

        in: gram fat
        out: delay in increase BGC
        '''

        fat_effect = int(g * self.FAT_INFLUENCE)
        fat_infl = fat_effect * [0]

        return fat_infl

    def protein_rule(self, g):
        '''
        effect of X gram protein on the BGC

        in: gram protein
        out: incrase in BGC
        '''

        prot_effect = int(g * self.PROTEIN_INFLUENCE)
        protein_infl = prot_effect * [0]

        return protein_infl

    def moderate_exercise_rule(self):
        '''
        effect of X minutes moderate exercise on the BGC

        in: duration in min of moderate exercise
        out: decrease in BGC
        '''

        mod_infl = [-5,-10,-15,-20]

        # fill up to length 144
        val = mod_infl[-1]
        fill_list = [val] * (144 - len(mod_infl))
        mod_infl = mod_infl + fill_list
        return mod_infl

    def intense_exercise_rule(self):
        '''
        effect of X minutes of intense exercise on the BGC

        in: duration in min of intense exercise
        out: decrase in BGC
        '''

        int_infl = [5,10,15,20,25]
        # fill up to length 144
        val = int_infl[-1]
        fill_list = [val] * (144 - len(int_infl))
        int_infl = int_infl + fill_list
        return int_infl

    def insulin_rule(self, units):
        '''
        effects of X insulin units on the BGC

        in: units insulin
        out: decrease influence
        '''

        ins_infl = self.INS_DELAY * [0]

        effect_duration = self.INS_DURATION - self.INS_DELAY
        total_decrease = -units * self.KF_FACTOR

        ins_step_size = total_decrease / effect_duration

        for i in range(1, effect_duration + 1):
            ins_infl.append(ins_step_size * i)

        # fill up to length 144
        val = ins_infl[-1]
        fill_list = [val] * (144 - len(ins_infl))
        ins_infl = ins_infl + fill_list

        return ins_infl

    def calculate_correction_ins(self, predictions):
        '''
        given that the blood glucose levels will be too high in the future, calculate the correct amount
        that will be recommended to the patient

        in: predicted time series of blood glucose concentrations
        out: amount of insulin units (fast) that should be injected
        '''

        # duration of insulin 180 mins, so recommend an amount such that blood glucose is optimal after that duration
        target = predictions.master_list[18]

        # calculate diffscore
        diff = target - self.OPTIMAL_BGC

        # calculate amount of insulin units to be injected
        units = diff / self.KF_FACTOR

        return units

    def calculate_correction_sugar(self, predictions):
        '''
        given that the blood glucose level will be too low in the future, calculate the correct amount
        will be recommende to the patient

        in: predicted time series of blood glucose concentrations
        out: gram sugar that should be consumed
        '''

        # sugar duration is 60 minutes, but insulin takes longer effects, find some middle ground that works well
        target = predictions.master_list[10]

        # calculate diffscore
        diff = self.OPTIMAL_BGC - target

        # calculate amount of BE that should be eaten
        BEs = diff / self.BE_EF

        # calculate g sugar that should be eaten
        g = BEs * self.G_BE_EXCHANGE_FACTOR

        return g

    def causal_model(self, hypothesis):

        """
        function that specifies the observables that have to be checked given a hypothesis

        in: hypothesis
        out: observable
        """

        if hypothesis == 'food':
            observable = 'nutrition'
        elif hypothesis == 'insulin':
            observable = 'insulin'
        elif hypothesis == 'moderate_exercise' or hypothesis == 'intense_exercise':
            observable = 'exercise'

        return observable

    def check_hypothesis(self, hypothesis, finding):


        """
        given hypothesis and finding, return whether the finding supports the hypothesis or not

        in: hypothesis, finding
        out: result bool
        """

        if hypothesis == 'food':
            nutrition = finding
            sugar = nutrition[SUG]
            fast_carbs = nutrition[FCARB]
            slow_carbs = nutrition[SCARB]

            if sugar > 5 or fast_carbs > 5 or slow_carbs > 5:
                return True
            else:
                return False

        elif hypothesis == 'insulin':
            insulin = finding

            if insulin > 0:
                return True
            else:
                return False

        elif hypothesis == 'moderate_exercise':
            exercise = finding

            steps = exercise[STEP]
            hr = exercise[HR]
            mets = exercise[MET]

            if 20 < steps < 120 and 90 < hr < 120 and 3 < mets < 6:
                return True
            else:
                return False

        elif hypothesis == 'intense_exercise':
            exercise = finding

            hr = exercise[HR]
            steps = exercise[STEP]
            mets = exercise[MET]

            if steps > 120 and hr > 120 and mets > 6:
                return True
            else:
                return False