# LTS_RuleSystem.py
# =================
# 0.01.002  27-Oct-2005  jmk  Converted to a child object of LTS_Allowables.
# 0.01.001  25-Oct-2005  jmk  Split off from find_lexicon_allowables.
# ---------------------

import codecs 
import pickle
import string
import os, sys
import time
    
import LTS_Allowables    
import LTS_IO

from Column import column
    


# --------------------------------------------------------------------------------------------------
class T (LTS_Allowables.T):



    # ----------------------------------------------------------------------------------------------
    def __init__ (self, unknown_phone = '_?_'):
        super(T,self).__init__()
        self.lts_rule_system = {}                           # central data structure of this object 
        self.unknown_phone_symbol = unknown_phone
        


    # ----------------------------------------------------------------------------------------------
    # Purpose:  Return a copy of the LTS rule system.                                               
    # Comment:  I used to return self.lts_rule_system directly, but don't anymore.                  
    #                                                                                               
    def GetRules (self): 
        
        answer = {}

        for lhs, rule_chain in self.lts_rule_system.items():
            answer[lhs] = rule_chain[:]
        return answer       
            


    # ----------------------------------------------------------------------------------------------
    # Purpose:  Return number of rules in LTS system.                                               
    #                                                                                               
    def GetNumberOfRules (self): 
        return sum (map ((lambda x: len(x)), self.lts_rule_system.values()))



    # ----------------------------------------------------------------------------------------------
    # Purpose:  Return a histogram of rule lengths.                                                 
    #                                                                                               
    def GetRuleHistogram (self): 

        answer = {}

        for lhs, rule_chain in self.lts_rule_system.items():
            for rule in rule_chain:
                L = rule_length  = len (string.join (rule[0],''))
                answer[L] = answer.get(L,0) + 1
        return answer       
    


    # ----------------------------------------------------------------------------------------------
    # Purpose:  Write a human-readable form of the LTS rules to a file.                             
    # Comment:  Since the caller isn't expected to know the internal phone names,                   
    #           this serves as a convenience wrapper around LTS_IO.WriteOutRules.                   
                                                                                                   
    def WriteOutRules (self, output_file, given_rule_system=None):
        if given_rule_system:
            LTS_IO.WriteOutRules (output_file, given_rule_system, self.GetPhoneNameInvTable())
        else:        
            LTS_IO.WriteOutRules (output_file, self.lts_rule_system, self.GetPhoneNameInvTable())
        return True
    
                                

    # ----------------------------------------------------------------------------------------------
    def WriteOutFestivalRules (self, output_filename='', given_rule_name='inst_lang', given_rule_system=None):
        

        # ------------------------------------------------------------------------------------------
        def WriteRules (outfile, rule_name):
            outfile.write ('\n')

            if given_rule_system:
                lts_rule_system = given_rule_system
            else:
                lts_rule_system = self.lts_rule_system

            lhs_symbol_list = lts_rule_system.keys()
            lhs_symbol_list.sort()    

            for lhs in lhs_symbol_list:
                lts_rule_chain = lts_rule_system[lhs][:]
                lts_rule_chain.reverse()    
                
                for rule in lts_rule_chain:
                    rule_context, prod_symbol_seq, count = rule
                    letter = rule_context[1].replace ("'","\"'\"")
                        
                    if letter not in string.punctuation:
                        prod_symbol_seq = map ((lambda x: self.phone_name_inverse_table.get(x,x)), prod_symbol_seq)
                        prod_symbol_str = string.join (prod_symbol_seq)
                        lhs_context_str = string.join (list (rule_context[0]))
                        rhs_context_str = string.join (list (rule_context[2]))
                            
                        lhs_context_str = lhs_context_str.replace ("'","\"'\"")
                        rhs_context_str = rhs_context_str.replace ("'","\"'\"")
                             
                        outfile.write ('  ( %s [ %s ] %s = %s )\n' \
                            %(lhs_context_str, letter, rhs_context_str, prod_symbol_str))
                            
            outfile.write ('\n')
            outfile.close()    
                
             
        if not output_filename:
            WriteRules (sys.stdout, given_rule_name)
        else:        
            output_file = codecs.open (output_filename, 'w', 'utf-8')
            WriteRules (output_file, given_rule_name)
            
        return True
    pass        
        


    # ----------------------------------------------------------------------------------------------
    # Purpse:   Save LTS rule system state information into a pickle file.                          
    #                                                                                               
    def PickleStateInfoRules (self, output_filename):
        
        crucial_state_info = (self.phone_name_inverse_table,
                              self.production_counts_table_1d, 
                              self.lts_rule_system)

            
        if string.find (output_filename, 'pkl') > -1:
            text_filename = output_filename.replace ('pkl', 'txt')
        else:
            text_filename = output_filename + '.txt'
                
        #outfile = file (text_filename, 'w')
        #outfile.write ('%s' %(str(crucial_state_info)))
        #outfile.close()
            
        outfile = file (output_filename, 'w')
        pickle.dump (crucial_state_info, outfile)
        outfile.close()
            
        return True
    pass



    # ----------------------------------------------------------------------------------------------
    # Purpose:  Read the LTS state information pickle file into memory.                             
    #                                                                                               
    def LoadStateInfoRules (self, input_filename):
        
        infile = file (input_filename, 'r')
        crucial_state_info = pickle.load (infile)
        infile.close()    

        (self.phone_name_inverse_table,
         self.production_counts_table_1d, 
         self.lts_rule_system) = crucial_state_info
            
        return crucial_state_info
    pass



    # ----------------------------------------------------------------------------------------------
    def GetRulesByCount (self):
    
        rule_counts = []
        lhs_symbol_list = self.lts_rule_system.keys()

        for lhs in lhs_symbol_list:
            lts_rule_chain = self.lts_rule_system [lhs]
            for rule in lts_rule_chain:
                rule_context, rhs_symbol_seq, application_count = rule 
                rule_counts.append ((application_count, rule))
                        
        rule_counts.sort (reverse=True)
        return rule_counts
    pass
        
            

    # ----------------------------------------------------------------------------------------------
    def ThresholdRules (self, threshold_value = 0):

        # Check an early exit conditions.

        if threshold_value <= 0:  
            return self.lts_rule_system.copy(), self.GetNumberOfRules()

        
        # Create a reduced rule system by adding those rules   
        # with application counts above or equal the threshold.

        lhs_symbol_list = self.lts_rule_system.keys()

        reduced_rule_system = {}
        num_rules_in_system = 0
        num_chars_in_system = 0

        for lhs in lhs_symbol_list:
            lts_rule_chain = self.lts_rule_system [lhs]
                
            for rule in lts_rule_chain:
                rule_context, rhs_symbol_seq, count = rule 
                    
                if count >= threshold_value:    
                    lhs = rule[0][1]
                    if not reduced_rule_system.has_key (lhs):
                        reduced_rule_system[lhs] = []
                    reduced_rule_system[lhs].append (rule)
                    num_rules_in_system += 1
                    num_chars_in_system += len (rule[0][0]) + len (rule[0][2])
  
        num_chars_in_system += len (reduced_rule_system)

        return reduced_rule_system, num_rules_in_system, num_chars_in_system
    pass
 


    # ------------------------------------------------------------------------------------------
    # Comment: If the letter can't be predicted return () rather than '?'
        
    def PredictLetter (self, given_word, index, lts_rule_system=None, invert_phone_names=True, verbose=False):

        if not lts_rule_system:
            lts_rule_system = self.lts_rule_system

        letter = given_word [index]
        rule_chain_for_letter = lts_rule_system.get (letter,[])
            
        #rule_chain_for_letter = self.lts_rule_system.get (letter,[])
        #rule_chain_for_letter.reverse()
        #print '--', index, letter, given_word
        #print '--', rule_chain_for_letter
        #for item in lts_rule_system:
        #    print item, lts_rule_system[item]
                
        all_matches = []   
            
        """
        if verbose == 2 and len (rule_chain_for_letter) > 1:
            print given_word 
            for one_rule in rule_chain_for_letter:
                print '   ', one_rule
            print
        """
                    
        N = num_rules_for_letter = len (rule_chain_for_letter)
            
        # Scan rules from most specific to least specific.

        for i in range (N,0,-1):
            one_rule   = rule_chain_for_letter[i-1]
            lhs, rhs   = one_rule[:2]
            prod_count = one_rule[2]   
            left_len   = len (lhs[0])
            right_len  = len (lhs[2])
            beg_pos    = index - left_len
            end_pos    = index + right_len
            left_side  = given_word [beg_pos : index]
            right_side = given_word [index+1 : end_pos+1]
            context    = (left_side, letter, right_side)
            
            if verbose == 2 and len (rule_chain_for_letter) > 1:
                print letter, context == lhs, one_rule, context, lhs

            if context == lhs:
                if invert_phone_names:
                    phone_names = tuple (map ((lambda x: self.phone_name_inverse_table.get(x,x)), rhs))
                    all_matches.append ((phone_names, prod_count, i))
                else:        
                    all_matches.append ((rhs, prod_count, i))
                  
        
        if all_matches: 
            prediction = all_matches[0][0]
        else:
            prediction = (self.unknown_phone_symbol,)
                    
        return prediction, all_matches
    pass        

       

    # --------------------------------------------------------------------------------------------------
    def PredictOneWordPronun (self, given_charseq, given_lts_rule_system=None, invert_phone_names=True, verbose=False):

        padded_charseq = ['#'] + list (given_charseq) + ['#']
        padded_word    = string.join (padded_charseq,'')    
        prediction     = []
        pred_phoneseq  = []  

        if not given_lts_rule_system:
            given_lts_rule_system = self.lts_rule_system
                
        for i, ch in enumerate (padded_charseq [1:-1]):
            if ch not in string.whitespace:
               #predicted_phone, all_pred_phones = self.PredictLetter (padded_charseq, i+1, given_lts_rule_system, invert_phone_names, verbose=2) 
                predicted_phone, all_pred_phones = self.PredictLetter (padded_word, i+1, given_lts_rule_system, invert_phone_names, verbose) 
                prediction.append ((ch, predicted_phone, all_pred_phones))
                #print i, ch, ord(ch), predicted_phone, all_pred_phones
                #if predicted_phone == (self.unknown_phone_symbol,): sys.exit()    

        for letter, best_phoneseq, all_phoneseqs in prediction:
            if best_phoneseq: 
                pred_phoneseq.append (string.join (best_phoneseq))

        return pred_phoneseq, prediction 
    pass
        

 
    # --------------------------------------------------------------------------------------------------
    def PredictMultipleWordPronuns (self, given_charseq, verbose=False):


        # ----------------------------------------------------------------------------------------------
        def FindAllSolutions (prediction):
            
            def DescendOneLevel (curr_solution, level):
                
                if level >= len (prediction): 
                    all_solutions.append (curr_solution[:])
                    curr_solution.pop()    
                    return

                letter, best_phoneseq, all_phoneseqs = prediction [level]
                    
                for one_phoneseq, score, rule_num in all_phoneseqs:
                    curr_solution.append ((one_phoneseq, score))
                    DescendOneLevel (curr_solution, level+1)
                        
                if curr_solution: curr_solution.pop()
            pass    
                
            pronun_list = []
            all_solutions = []     
            DescendOneLevel ([], 0)
                
            for one_soln in all_solutions:
                rhs_seq = column (one_soln, 0)
                phoneseq = []    
                for rhs in rhs_seq: 
                    if rhs: phoneseq.append (string.join(rhs))
                score   = sum (column (one_soln, 1))
                pronun_list.append ((score, string.join(phoneseq)))
                    
                             
            # sort words by score in _ascending_ order because lower counts     
            # represent more specialzed conditions identified by letter context.
                
            pronun_list.sort (reverse=False)    
            answer = [(pronun, count) for (count, pronun) in pronun_list]

            return answer
        pass        


        pred_phoneseq, prediction = self.PredictOneWordPronun (given_charseq)
        all_solutions = FindAllSolutions (prediction)
            
        if verbose and len (all_solutions) > 0:
            for soln in all_solutions:
                print 'Word soln:', soln
            print
        

        # do this because FindAllSolutions doesn't get pronunciations
        # when some of the letters go to '?'                         
            
        answer = [string.join(pred_phoneseq)] + column (all_solutions[1:])
        return answer
    pass
        
         
 
# end class T.
# ------------
        


