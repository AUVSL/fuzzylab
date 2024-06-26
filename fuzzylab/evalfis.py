import numpy as np
from .evalmf import evalmf
from .sugfis import sugfis
from .defuzz import defuzz

def evalfis(fis, user_input, rule_firing=False, num_points = 101):

    if type(user_input) is not np.ndarray:
        user_input = np.asarray([user_input])

    if user_input.ndim == 1:
        user_input = np.asarray([user_input])

    # input = multiple entries*input numbers

    m, n = user_input.shape
    num_inputs = n #add 20240624
    #num_inputs = len(fis.Inputs)

    #if m is num_inputs and n is not num_inputs:
    #    user_input = user_input.transpose()

    output = np.zeros((len(user_input), len(fis.Outputs)))

    rule_input = fuzzify_input(fis, user_input) #add 20240624
    firing_strength = eval_firing_strength(fis, rule_input) #add 20240624
    if fis.Type == 'sugeno':
        print("Sugeno to be completed in the next version")
    elif fis.Type == 'mamdani':
        rule_output = eval_rules_mamdani(fis, firing_strength, num_points)
        fuzzy_output = aggregate_output_mamdani(fis, rule_output)
        output = defuzzify_output_mamdani(fis, fuzzy_output)
    
    ''' old code, use for loops
    for i in range(len(user_input)):
        rule_input = fuzzify_input(fis, user_input[i])

        firing_strength = eval_firing_strength (fis, rule_input)
        
        if fis.Type is sugeno: #change type(fis)->fis.Type
            rule_output = eval_rules_sugeno(fis, firing_strength, user_input[i])
            fuzzy_output = aggregate_output_sugeno (fis, rule_output)
            output[i] = defuzzify_output_sugeno (fis, fuzzy_output)
        
        elif fis.Type is mamdani: #add 20240624
            rule_output = eval_rules_mamdami(fis, firing_strength, user_input[i])
            fuzzy_output = aggregate_output_mamdani(fis, rule_output)
            output[i] = defuzzify_output_mamdani(fis, fuzzy_output)
    '''
    if output.shape == (1,1):
        output = output[0,0]

    if rule_firing:
        return output, firing_strength
    else:
        return output


def fuzzify_input(fis, user_input):
    ##test
    #user_input = np.asarray([[0.6],[0.5]])

    num_rules  = len(fis.Rules)
    num_inputs = len(fis.Inputs)
    num_pxs = user_input.shape[0] #add 20240620
    rule_input = np.zeros((num_rules, num_inputs, num_pxs)) #add 20240624
    #rule_input = np.zeros((num_rules, num_inputs))

    # For each rule i and each input j, compute the value of mu
    # in the result. 

    for i in range(num_rules):
        antecedent = fis.Rules[i].Antecedent
        for j in range(num_inputs):
            crisp_x = user_input[:, j] #add 20240624
            #crisp_x = user_input[j]

            mf_index = antecedent[j]
            if mf_index >=0:
                mf = fis.Inputs[j].MembershipFunctions[mf_index]
                mu = evalmf (mf, crisp_x)
                #print('mu = ', mu)
            else: #add 20240620
                #mu = 1 #add 0118
                mu = np.ones((1,1,num_pxs))  #add 20240620
            # Store the fuzzified input in rule_input.    
            rule_input[i, j, :] = mu
            #print(mu)
    
    #print("Rule input test = ", rule_input.shape)
    #print("Rule input = ", rule_input)
    return rule_input
 

def eval_firing_strength (fis, rule_input):
    ## Test
    num_rules = len(fis.Rules)
    num_inputs = len(fis.Inputs)
    num_pxs = rule_input.shape[2] #add 20240624

    # Initialize output matrix to prevent inefficient resizing.
    firing_strength = np.zeros ((num_pxs, num_rules)) #add 20240624
    #firing_strength = np.zeros (num_rules)
 
    ## For each rule
    ##    1. Apply connection to find matching degree of the antecedent.
    ##    2. Multiply by weight of the rule to find degree of the rule.
    

    for i in range(num_rules):
        rule = fis.Rules[i]
        # Collect mu values for all input variables in the antecedent.
        antecedent_mus = []
        for j in range(num_inputs):
            if rule.Antecedent[j] >= 0:
                mu = rule_input[i, j, :] #add 20240624
                mu_reshape = mu.reshape(num_pxs, 1) #add 20240624
                #mu = rule_input[i, j]
                antecedent_mus.append(mu_reshape) #add 20240624
                #antecedent_mus.append(mu)

        output_mus = np.hstack(antecedent_mus)

        #print("antecedent_mus = ", output_mus)
        # Compute matching degree of the rule.
        if rule.Connection == 1:
            connect = fis.AndMethod
        else:
            connect = fis.OrMethod

        if connect == 'prod':
            firing_strength[:, i] = rule.Weight * np.prod(antecedent_mus, axis = 1) #add 20240620
            #firing_strength[i] = rule.Weight * np.prod(antecedent_mus)
        elif connect == 'min':
            firing_strength[:, i] = rule.Weight * np.min(output_mus, axis = 1) #add min 20240620

    return firing_strength



def eval_rules_mamdani(fis, firing_strength, num_points): #add 20240624

    num_rules = len(fis.Rules)
    num_outputs = len(fis.Outputs)
    num_pxs = firing_strength.shape[0]
    
    # Initialize output matrix to prevent inefficient resizing.
    rule_output = np.zeros((num_points, num_rules * num_outputs, num_pxs))
    #rule_output = np.zeros((num_points, num_rules * num_outputs))   
    
    # Compute the fuzzy output for each (rule, output) pair:
    #   1. Apply the FIS implication method to find the fuzzy outputs
    #      for the current (rule, output) pair.
    #   2. Store the result as a column in the rule_output matrix.
    
    for i in range(num_rules):
        rule = fis.Rules[i]
        rule_matching_degree = firing_strength[:, i].reshape(1, num_pxs) #add 20240624
        #rule_matching_degree = firing_strength[i]

        #if rule_matching_degree != 0:
        for j in range(num_outputs):
            mf_index = rule.Consequent[j] - 1
            out_range = fis.Outputs[j].Range
            mf = fis.Outputs[j].MembershipFunctions[mf_index]
            x = np.linspace(out_range[0], out_range[1], num_points)
            fuzzy_out = evalmf(mf, x)
            fuzzy_out = fuzzy_out.reshape(num_points, 1)
            if fis.ImplicationMethod == 'min':
                fuzzy_out = np.minimum(rule_matching_degree, fuzzy_out)

            rule_output[:, (j - 1) * num_rules + i, :] = fuzzy_out

    return rule_output


def aggregate_output_mamdani(fis, rule_output):
    num_rules = len(fis.Rules)
    num_outputs = len(fis.Outputs)
    num_points = rule_output.shape[0]
    num_pxs = rule_output.shape[2]

    # Initialize output matrix to prevent inefficient resizing.
    fuzzy_output = np.zeros((num_points, num_outputs, num_pxs))

    # Compute the ith fuzzy output values, then store the values in the
    # ith column of the fuzzy_output matrix.
    for i in range(num_outputs):
        indiv_fuzzy_out = rule_output[:, i*num_rules : (i+1)*num_rules, :]
        if fis.AggregationMethod == 'max':
            agg_fuzzy_out = np.max(indiv_fuzzy_out, axis=1)
        fuzzy_output[:, i, :] = agg_fuzzy_out

    return fuzzy_output


def defuzzify_output_mamdani(fis, fuzzy_output):

    num_outputs = len(fis.Outputs)
    num_points = len(fuzzy_output)
    num_pxs = fuzzy_output.shape[2]
    output = np.zeros((num_pxs, num_outputs))

    for i in range(num_outputs):
        out_range = fis.Outputs[i].Range
        x = np.linspace(out_range[0], out_range[1], num_points)
        y = fuzzy_output[:, i, :]
        output[:, i] = defuzz(x, y, fis.DefuzzificationMethod)

    return output



def eval_rules_sugeno(fis, firing_strength, user_input):

    num_rules = len(fis.Rules)
    num_outputs = len(fis.Outputs)

    # Initialize output matrix to prevent inefficient resizing.
    rule_output = np.zeros ((3, num_rules * num_outputs))   #0115 2->3
    #print(user_input)
    # Compute the (location, height) of the singleton output by each
    # (rule, output) pair:
    #   1. The height is given by the firing strength of the rule, and
    #      by the hedge and the not flag for the (rule, output) pair.
    #   2. If the consequent membership function is constant, then the
    #      membership function's parameter gives the location of the
    #      singleton. If the consequent membership function is linear,
    #      then the location is the inner product of the the membership
    #      function's parameters and the vector formed by appending a 1
    #      to the user input vector.

    for i in range(num_rules):
        rule = fis.Rules[i]
        rule_firing_strength = firing_strength[i]

        if rule_firing_strength != 0:
            for j in range(num_outputs):
                
                mf_index = rule.Consequent[j]

                height = rule_firing_strength

                # Compute the singleton location for this (rule, output) pair.

                mf = fis.Outputs[j].MembershipFunctions[mf_index]

                if mf.Type == 'constant':
                    location = mf.Parameters
                    width = 0
                else: #0115 add
                    location = mf.Parameters[1] #0115 add
                    width = mf.Parameters[2]-mf.Parameters[0] #0115 add
                # Store result in column of rule_output corresponding
                # to the (rule, output) pair.   

                rule_output[0, (j - 1) * num_rules + i] = location
                rule_output[1, (j - 1) * num_rules + i] = height
                rule_output[2, (j - 1) * num_rules + i] = width #0115 add
    
    #print(rule_output)
    return rule_output


def aggregate_output_sugeno(fis, rule_output):

    fuzzy_output = []
    num_outputs = len(fis.Outputs)
    num_rules = len(fis.Rules)

    # For each FIS output, aggregate the slice of the rule_output matrix,
    # then store the result as a structure in fuzzy_output.

    for i in range(num_outputs):
        unagg_output = rule_output[:, i*num_rules : (i+1)*num_rules]
        aggregated_output = aggregate_fis_output(fis.AggregationMethod, unagg_output)
        fuzzy_output.append(aggregated_output)

    return np.asarray(fuzzy_output)


#----------------------------------------------------------------------
# Function: aggregate_fis_output
# Purpose:  Aggregate the multiple singletons for one FIS output.
#----------------------------------------------------------------------

def aggregate_fis_output(fis_aggmethod, rule_output):

    # Initialize output matrix (multiple_singletons).
    rule_output = np.transpose(rule_output)
    mult_singletons = rule_output[rule_output[:,0].argsort()]

    # If adjacent rows represent singletons at the same location, then
    # combine them using the FIS aggregation method.

    for i in range(len(mult_singletons) - 1):
        if mult_singletons[i,0] == mult_singletons[i+1, 0]:
            if fis_aggmethod == 'sum':
                mult_singletons[i + 1, 1] = mult_singletons[i, 1] + mult_singletons[i + 1, 1]

            mult_singletons[i, 1] = 0

    # Return the transpose of the matrix after removing 0-height
    # singletons.

    mult_singletons = np.transpose(remove_null_rows(mult_singletons))

    return mult_singletons


def remove_null_rows(x):
    y = []
    for i in range(len(x)):
        if x[i, 1] != 0:
            y.append(x[i])

    return np.asarray(y)


def defuzzify_output_sugeno(fis, aggregated_output):

    num_outputs = len(fis.Outputs)
    output = np.zeros(num_outputs)

    for i in range(num_outputs):
        next_agg_output = aggregated_output[i]
        x = next_agg_output[0]
        y = next_agg_output[1]
        w = next_agg_output[2]
        output[i] = defuzz(x, y, w, fis.DefuzzificationMethod)

    return output