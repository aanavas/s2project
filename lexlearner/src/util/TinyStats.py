# TinyStats.py
# ------------
# 0.01.003  08-Jun-2005  jmk  Added ComputeMutualInformation.
# 0.01.002  11-May-2004  jmk  Added ComputeEntropy.
# 0.01.001  15-Mar-2004  jmk  Created.
# ---------------------

import math


# ----------------------------------------------------------------------------------------
def column (array, col=0): return map ((lambda x: x[col]), array)



# ----------------------------------------------------------------------------------------
def ave (input_list):
    return float(sum(input_list)) / float (max (1,len(input_list)))
pass
    

# ----------------------------------------------------------------------------------------
def stdev (input_list):

    N = len (input_list)
    if N == 0: return (0,0,0)
    
    average = ave (input_list)
    total_difference = 0.0
        
    for value in input_list:
        diff = value - average
        total_difference += diff * diff

    if N > 1:
        standard_deviation = math.sqrt (total_difference / float(N-1))
    else:
        standard_deviation = 0.0
                    
    return N, average, standard_deviation
pass            




# ----------------------------------------------------------------------------------------
def ComputeEntropyFromSymbolCounts (symbol_count_list, exclusion_list = []):
    
    entropy     = 0.0
    total_count = 0.0
        
    for symbol, count in symbol_count_list:
        if count > 0 and symbol not in exclusion_list: total_count += count

          
    for symbol, count in symbol_count_list:
        if count > 0 and symbol not in exclusion_list:
            symbol_prob    = count / total_count
            symbol_logprob = math.log (symbol_prob)              
            entropy += symbol_prob * symbol_logprob
                
    entropy = abs (entropy)                     # more stable than negation when entropy = 0
    entropy_base2 = entropy / math.log(2)
        
    return entropy_base2
pass



# ----------------------------------------------------------------------------------------
def ComputeEntropy (list_of_symbols):

    S = symbol_count_tbl = {}
    
    for symbol in list_of_symbols:
        S[symbol] = S.get(symbol,0) + 1

    return ComputeEntropyFromSymbolCounts (S.items())            
pass
    


# ----------------------------------------------------------------------------------------
def ComputeMutualInformation (list_of_symbol_pairs):
    
    entropy_X  = ComputeEntropy (column (list_of_symbol_pairs,0))
    entropy_Y  = ComputeEntropy (column (list_of_symbol_pairs,1))
    entropy_XY = ComputeEntropy (list_of_symbol_pairs)
          
    #print entropy_X, entropy_Y, entropy_XY
    return entropy_X + entropy_Y - entropy_XY
pass        

        
       

