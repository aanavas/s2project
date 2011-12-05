# DynamicTimeWarp.py                                                                                
# ==================                                                                                
# 0.01.006  11-Nov-2006  jmk  Changed PrintBestPath to not assume the first items are null.         
# 0.01.005  13-Oct-2005  jmk  Added subst_table parameter.                                          
# 0.01.004  11-Apr-2004  jmk  Added AlignStringLists.                                               
# 0.01.003  02-Feb-2004  jmk  Added a client-callable cost function for {Ins, Del, Sub, Mat}.       
# 0.01.002  28-Jan-2004  jmk  Extracted from old program to put in a tools library. Commented alignment routine.
# 0.01.001  23-Oct-2001  jmk  Simple rountine for dynamic time warping of word sequences.           
# =====================                                                                             
# Things to do:                                                                                     
# - perform include N-best alignments                                                               
# - controllable beam search window                                                                 
# - DTW routine for real numbered vectors                                                           
# - search multiple references at the same time                                                     
# - split into interface and implementation                                                         
# - need to be able to treat pauses as zero cost insertions                                         
# --------------------------------------------------------------------------------------------------


import string
import sys, difflib
import ConfigPath
import Logger


# -------------------------------
# Use a global variable for now. 
# Later convert to an object with logging facilities.

global_text_logger = None
error_codes = ['INS', 'DEL', 'SUB']




# --------------------------------------------------------------------------------------------------
# Function: AlignStrings                                                                            
# Purpose:  Perform dynamic time warping on a pair of word strings.                                 
#           The string consist of whitespace-separated tokens.                                      
# Params:   reference_string  - correct string of words.                                            
#           hypothesis_string - hypothesized string of words.                                       
#           verbose - weather to log details or not.                                                
# Return:                                                                                           

def AlignStrings (reference_string, hypothesis_string, cost_table = [1,1,1,0], subst_table = {}, verbose = False):

    # Split the input strings into word (or 'token') lists.                  
    # Prepend the list with the emptry string. This makes things easier      
    # for the matching algorithm by keeping indicies consistent.             
    # For example, if the 2nd hypothesis word matches the 3rd reference word,
    # then the path information can be found in path_matrix[2,3].            

    return AlignStringLists (string.split (reference_string), string.split (hypothesis_string))
pass


# --------------------------------------------------------------------------------------------------
def AlignStringLists (ref_list, hyp_list, cost_table = [1,1,1,0], subst_table = {}, verbose = False):

    reference_word_list  = [''] + list (ref_list)
    hypothesis_word_list = [''] + list (hyp_list)

    path_matrix = ComputePathCostMatrix (reference_word_list, hypothesis_word_list, cost_table,  subst_table, verbose)
   #best_path   = FindSingleBackTrace   (reference_word_list, hypothesis_word_list, path_matrix, verbose)
    best_path_list = FindAllBestBackTraces (reference_word_list, hypothesis_word_list, path_matrix, verbose)


    """    
    if verbose:
        PrintBestPath (reference_word_list, hypothesis_word_list, best_path, verbose)
            
    L = len (best_path) - 1
    score = best_path[L][0]
        
    # remove offset introduced by prepending [''] to the ref and hyp lists  above
    for item in best_path:
        item[2] = (item[2][0]-1, item[2][1]-1)

    return score, best_path_list
    """
        
                

    # Note: have to create a fresh copy because the (i,j) index pair can refer to the same python object,
    #       and thus the subtraction can happen multiple times on the same thing for                     
    #           for item in best_path: item[2] = (item[2][0]-1, item[2][1]-1)                            
    #       which is a bug.                                                                              
         
    answer = []            
    for best_path in best_path_list:
        new_best_path = []

        # remove offset introduced by prepending [''] to the ref and hyp lists  above
        #for item in best_path:
        #    item[2] = (item[2][0]-1, item[2][1]-1)
                    
        for score, oper, (i,j) in best_path:
            new_item = [score, oper, (i-1,j-1)]
            new_best_path.append (new_item)    
        answer.append (new_best_path)

        if verbose:
            PrintBestPath (reference_word_list[1:], hypothesis_word_list[1:], new_best_path)



    L = len (best_path) - 1
    score = new_best_path[L][0]
        
    return score, answer
pass




# --------------------------------------------------------------------------------------------------
def PrintBestPath (ref_words_list, hyp_words_list, bestpath):

    #print 'REF', ref_words_list
    #print 'HYP', hyp_words_list
    #print 'BPa', bestpath

    str1 = 'REF  '
    str2 = 'HYP  '
    str3 = '     '    
    str4 = 'COST '    
         
    for arc in bestpath:
        timewarp = string.upper (arc[1])
        hyp_word = hyp_words_list [arc[2][0]]
        ref_word = ref_words_list [arc[2][1]]
        path_score = arc[0]    
        path_score_str = str(path_score)    

        if timewarp == 'INS': ref_word = ''
        if timewarp == 'DEL': hyp_word = ''
        if timewarp == 'MAT': timewarp = ''

        fieldwidth = max (len(hyp_word), len(ref_word), len(timewarp), len(path_score_str)) + 1

        str1 = str1 + string.ljust (ref_word, fieldwidth)
        str2 = str2 + string.ljust (hyp_word, fieldwidth)
        str3 = str3 + string.ljust (timewarp, fieldwidth)
        str4 = str4 + string.ljust (path_score_str, fieldwidth)    

            
    ref_utterance_length = len(ref_words_list)       
    word_error_rate      = float (path_score) / float (ref_utterance_length) * 100

    if global_text_logger:
        global_text_logger.write ('')
        global_text_logger.write ('%s' %(str1), Logger.Info_Level)
        global_text_logger.write ('%s' %(str2), Logger.Info_Level)
        global_text_logger.write ('%s' %(str3), Logger.Info_Level)
        global_text_logger.write ('%s' %(str4), Logger.Info_Level)
        global_text_logger.write ('WER: %2.2f (%i/%i)' %(word_error_rate, path_score, ref_utterance_length), Logger.Info_Level)
        global_text_logger.write ('%s' %('-----------------\n'), Logger.Info_Level)


pass



# --------------------------------------------------------------------------------------------------
# Function: AlignStrings.FindSingleBackTrace()                                                      
# Input:    ref_words   - correct (reference) word sequence                                         
#           hyp_words   - hypothesized (given) word sequence                                        
#           path_matrix - stores best path information for each lattice point                       
# Output:                                                                                           
# Comment:  Only need word lists to find the back track starting point.                             
#           Wouldn't need to do this if path_matrix was an array.                                   
# Example:                                                                                          
#   ref string: 'a chance of evening flurries later tonight'                                        
#  test string: 'a B of C evening flurries'                                                         

def FindSingleBackTrace (ref_words, hyp_words, path_matrix, verbose):

    # The backtrace starts at the point where DTW search finished. 
    # Initialize the indicies (i,j) and let M be a short form name.
    # Initialize the best path list with the termination point     
                                                                   
    M = path_matrix
    i = len (hyp_words) - 1 
    j = len (ref_words) - 1

    bestpath = [] #[['End', (i,j)]]

    # Follow the backpointers to coordinates (0,0)                                        
    # The bestpath list at this point has the labels offset by one from the coordinates.  
    # For example, ['Del', (6, 6)] means that a deletion operation labels the arc from    
    # (6,6) to the next node, which is (6,7).                                             
    # It's more natural to shift operations by one so that ['Del', (6, 7)] means we       
    # got to (6,7) by a deletion. Note that we get ['Mat', (1,1)] as the first element    
    # of the bestpath, interpreted as: the first word of the test string matches the      
    # first word of the reference string. This makes sense.                               

    while i>0 or j>0:
        if verbose and global_text_logger:
            global_text_logger.write ('backtracing %2i %2i  %s' %(i, j, str(M[i,j])), Logger.Detail_Level)

        # extract the backpoint coordinates and append to the best path list

        path_score = M[i,j][0]
        prev_node  = M[i,j][1][0]        
        path_oper  = prev_node[0]    
        path_node  = [path_score, path_oper, (i,j)]    
        i, j = prev_node[1]

        bestpath.append (path_node)


    # reverse list so that it reads forward in time

    bestpath.reverse()
        
    return bestpath
pass


# --------------------------------------------------------------------------------------------------
def FindAllBestBackTraces (ref_words, hyp_words, path_matrix, verbose):

    # The backtrace starts at the point where DTW search finished. 
    # Initialize the indicies (i,j) and let M be a short form name.
    # Initialize the best path list with the termination point     

    M = path_matrix
    i = len (hyp_words) - 1 
    j = len (ref_words) - 1

    work_queue    = [(i,j,[])]
    best_path_list = [] 

    # Follow the backpointers to coordinates (0,0)                                        
    # The bestpath list at this point has the labels offset by one from the coordinates.  
    # For example, ['Del', (6, 6)] means that a deletion operation labels the arc from    
    # (6,6) to the next node, which is (6,7).                                             
    # It's more natural to shift operations by one so that ['Del', (6, 7)] means we       
    # got to (6,7) by a deletion. Note that we get ['Mat', (1,1)] as the first element    
    # of the bestpath, interpreted as: the first word of the test string matches the      
    # first word of the reference string. This makes sense.                               
    # Example:
    # 3  2 - [4, [['Ins', (2, 2)], ['Sub', (2, 1)]]]

        
    while work_queue:
        #print
        #print 'WQ - ', i, j, len(work_queue), work_queue
        i, j, best_path = work_queue.pop(0)
        #print 'BP - ', i, j, len(best_path), best_path
        #print 'PL - ', i, j, len(best_path_list)


        if i>0 or j>0:
            if verbose and global_text_logger:
                global_text_logger.write ('backtracing %2i %2i  %s' %(i, j, str(M[i,j])), Logger.Detail_Level)

            path_score = M[i,j][0]
            
            for prev_node in M[i,j][1]:
                path_oper  = prev_node[0]    
                path_node  = [path_score, path_oper, (i,j)]
                new_best_path = best_path[:]        
                new_best_path.append (path_node)
                prev_i, prev_j = prev_node[1]
                work_queue.append ((prev_i, prev_j, new_best_path))        
        elif i == 0 and j == 0:
            best_path_list.append (best_path)



    # reverse list so that it reads forward in time
        
    for bp in best_path_list:
        bp.reverse()
            
    #print            
    #for bp in best_path_list:
    #    print bp
    #print            


    return best_path_list
pass





# -----------------------------------------------------------------------------------------
# Function: AlignStrings.ComputePathMatrix()
# Purpose:  Compute minimal cost alignment between a pair of word sequences using DTW.
# Input:    ref_word_list - list of (correct) tokens
#           hyp_word_list - list of (to test) tokens
# Return:   path cost matrix M
# Describe: This implements full beamwidth DTW using immediate neighbour (3 point) local search.

def ComputePathCostMatrix (ref_word_list, hyp_word_list, cost_table, subst_table, verbose):

    print_log_info = verbose and global_text_logger
        

    # Make costs configurable.
    Ins_Cost   = cost_table[0]      # 1
    Del_Cost   = cost_table[1]      # 1
    Sub_Cost   = cost_table[2]      # 1
    Match_Cost = cost_table[3]      # 0


    # Define I and J as shortform names for the word list lengths
    # The score index (s) is ...
    
    I = len (hyp_word_list)
    J = len (ref_word_list)
        
    # Create cost matrix M. 
    # Represent it as a table mapping 2D coordinate (lattice points)
    #   to cost information structures.
    # Matrix description:
    #   - domain: 2D (i,j) coordinate representing pairing of reference and hypothesis tokens
    #       - i = index of hypothesis word (x-axis)
    #       - j = index of reference  word (y-axis)
    #   - range: information structure
    #       - Ex. (2,4) -> [3, [['Del', (2, 3)], ['Subst', (1, 3)]]]
    #       - Strucure: (score, list of (opcode, coord) pairs)
    #         - score is the best partial-path score to that point. Integer or real number.
    #         - the opcode string defines the operation ['Del', 'Ins', 'Subst', 'Match']
    #         - the coordinate is a back-pointer to the previous lattice point in the candidate path
    #       - A list of (opcode, coord) pairs is required to support cases where multiple paths
    #         lead to the same best (minimal) partial score. This often happens in string comparisons.

    M = {}
    Sc = score_index     = 0
    Pa = path_info_index = 1
                                
    # Initialize the path cost matrix                                                 
    # -------------------------------                                                 
    # 1. Define the matrix at the origin (0,0) to be a token match with path cost zero
    #    and that the path points back to itself.                                     
    # 2. Fill the y-axis boundary, ie. M[(0,j)]. These are reached from the origin    
    #    through deletion operations.                                                 
    # 3. Fill the x-axis boundary, ie. M[(i,0)]. These are reached from the origin    
    #    through insertion operations.                                                

    M[(0,0)] = (0, ['Mat',(0,0)])
    for j in range(1,J): M[(0,j)] = (M[0,j-1][Sc] + Del_Cost, [['Del', (0,j-1)]])
    for i in range(1,I): M[(i,0)] = (M[i-1,0][Sc] + Ins_Cost, [['Ins', (i-1,0)]])

    # This is a full beamwidth search. It fills all matrix entries.
    # Outer loop: run through hypothesis tokens                    
    # Inner loop: run through reference tokens                     
    #
    # At each step we consider three ways to reach the current lattice point.
    #   1. (i,j-1)   - from below, a Del operation                           
    #   2. (i-1,j)   - from the left, an Ins operation                       
    #   3. (i-1,j-1) - from the diagonal, a Match or Subst operation         
    #
    # Array variables of length 3 are used to represent the possibilities.                       
    #   path_cost is initialized to a place holder value -1.                                     
    #   path_oper is fixed for the 1st two cases. The third case is evaluated each iteration.    
    #   path_prev is a back-pointer to the previous lattice point corresponding to the operation.

    path_cost = [-1,-1,-1]
    path_oper = ['Ins', 'Del', 'Match or Subst']
                 
    for i in range(1,I):
        for j in range(1,J):
            
            # Define the three the back pointers and update the path costs.  
            # needed to get here by either deletions or insertion operations.

            path_prev    = [(i-1,j), (i,j-1), (i-1,j-1)]
            path_cost[0] = M[i-1,j][Sc] + Ins_Cost
            path_cost[1] = M[i,j-1][Sc] + Del_Cost
             
            # Determine the cost for the third case, traversing the diagonal from (i-1,j-1).
            # It will either be a Mat or a Subst error.                                     

            if hyp_word_list[i] == ref_word_list[j]:
                path_cost[2] = M[i-1,j-1][Sc] + Match_Cost
                path_oper[2] = 'Mat'
            else:
                hyp = hyp_word_list[i]    
                ref = ref_word_list[j]
                key = (ref,hyp)    
                cost = subst_table.get(key,Sub_Cost)      
                #print key, cost, subst_table.has_key(key)    
                path_cost[2] = M[i-1,j-1][Sc] + cost
                path_oper[2] = 'Sub'     
                    

            # Find the minimim path cost to this point.                                               
            # Update M[i,j] with this score and add a list skeleton for the candidate path operations.

            min_cost = min(path_cost)
            M[i,j] = [min_cost,[]]

            # Check all three cases. For each case that matches the minimal score to this point    
            # update the path information structure with the corresponding opcode and back pointer.

            for k in range(0,3):
                if path_cost[k] == min_cost:
                    M[i,j][Pa].append ([path_oper[k], path_prev[k]])

            if print_log_info:
                global_text_logger.write ('%2i %2i - %s' %(i, j, str(M[i,j])), Logger.Detail_Level)
                    
        pass
        if print_log_info: global_text_logger.write('', Logger.Detail_Level)
    pass
    
    # Return the path cost matrix. The best path is not reconstructed in this function.

    return M
pass




# ------------------------
if __name__ == '__main__':

    global_text_logger = Logger.T()    
    global_text_logger.SetVerbosityLevel (2,2)
        

    # -----------------
    def RunSmallTest():
        subs_table = {}
        refseq  = ('AH', 'CH')
        hypseq = ['EY','CH','EY']   

       #paths = AlignStringLists (refseq, hypseq, cost_table=[2,2,1,0], verbose=True)
        paths = AlignStringLists (refseq, hypseq, verbose=False)

        print
        print 'Answer', paths
        print

        PrintBestPath (refseq, hypseq, paths[1][0])
    pass


    RunSmallTest()

