# LTS_Allowables.py                                                     
# =================                                                     
# 0.02.002  07-May-2007  jmk  Take log10 from math instead of numpy.    
# 0.02.001  14-Mar-2007  jmk  Revised to support utf-8.                 
# 0.01.002  13-Nov-2005  jmk  Rewrote recomputeProductionCounts().      
# 0.01.001  23-Oct-2005  jmk  Split off from find_lexicon_allowables.   
# ---------------------                                                 

import codecs
import pickle    
import string
import StringIO    
import os, sys
import time

import ConfigPath
import DictionaryIO    
import DynamicTimeWarpExperimental
import LTS_IO    

import LTS_Allowables_config as Config
from   Column import column
from   math import log10


    

# --------------------------------------------------------------------------------------------------
class T(object):


    # ----------------------------------------------------------------------------------------------
    # production_counts_table_1d: ocurance count for each letter->phone production, if alignments are unique 
    # current_word_alignments: one or more alignments are appended for each word, as words are encountered
         
    def __init__ (self):
        self.production_counts_table_2d = {}    # maps Table [lhs][rhs] -> integer 
        self.production_counts_table_1d = {}    # maps Table [(lhs,rhs)] -> integer
        self.word_alignments_index_tbl  = {}    # maps Table [charseq] -> integer  
        self.current_word_alignments    = []    # list of [charseq, phoneseq, alignment_info]
        self.phone_name_inverse_table   = {} 
        self.phone_name_disguise_table  = {}
            

    # ----------------------------------------------------------------------------------------------
    def WriteAllowablesFile (self, scheme_filename = 'allowables.scm'):
        DictionaryIO.WriteProductionsToSchemeFile (scheme_filename, 
                                                   self.production_counts_table_1d,
                                                   self.phone_name_inverse_table)
        return True


    # ----------------------------------------------------------------------------------------------
    def WriteProductionsSummary (self, output_file):
        
        LTS_IO.WriteProductionsSummary (output_file, 
                                        self.production_counts_table_1d, 
                                        self.phone_name_inverse_table)
        return True 


    # ----------------------------------------------------------------------------------------------
    def PickleStateInfoAlignment (self, output_filename):
        
        crucial_state_info = (self.production_counts_table_1d, 
                              self.current_word_alignments,
                              self.phone_name_inverse_table)

        outfile = file (output_filename, 'w')
        pickle.dump (crucial_state_info, outfile)
        outfile.close()    
        return True    


    # ----------------------------------------------------------------------------------------------
    def LoadStateInfoAlignment (self, input_filename):
        
        infile = file (input_filename, 'r')
        crucial_state_info = pickle.load (infile)
        infile.close()    

        (self.production_counts_table_1d, 
        self.current_word_alignments,
        self.phone_name_inverse_table) = crucial_state_info
            
        self.phone_name_disguise_table = {}
        for key, val in self.phone_name_inverse_table.items():
            self.phone_name_disguise_table[val] = key
            
        return crucial_state_info
    pass

       

    # ----------------------------------------------------------------------------------------------
    def GetPhoneNameInvTable (self):
        return self.phone_name_inverse_table


        
    # ----------------------------------------------------------------------------------------------
    def SetPhoneNameInvTable (self, given_table):
        
        self.phone_name_inverse_table  = given_table
        self.phone_name_disguise_table = {}

        for key, val in self.phone_name_inverse_table.items():
            self.phone_name_disguise_table[val] = key
 
        return True    



    # ----------------------------------------------------------------------------------------------
    def UpdateOneProduction (self, lhs_symbol, rhs_symbols, count=1):
        
        L = lhs_symbol
        R = rhs_symbols        
        pct = self.production_counts_table_2d
            
        if pct.has_key (lhs_symbol):
            pct[L][R] = pct[L].get(R,0) + count
        else:
            pct[L] = {rhs_symbols: count}
            
        return True
                              

    # ----------------------------------------------------------------------------------------------
    def UpdateProductionsInSolution (self, charseq, phoneseq, found_solutions):
        
        self.current_word_alignments.append ((charseq, phoneseq, found_solutions))    
        self.production_counts_table_1d = self.RecomputeProductionCounts (break_ties=True)
        
        if found_solutions and found_solutions[0] and found_solutions[0][1]:
            for item in found_solutions[0][1]:
                lhs, rhs, curr_count = item    
                self.UpdateOneProduction (lhs, rhs)

        return True
     


    # ----------------------------------------------------------------------------------------------
    def HasProduction (self, lhs_symbol, rhs_symbols):
        
        L = lhs_symbol
        R = rhs_symbols        
        pct = self.production_counts_table_2d
            
        return pct.has_key(L) and pct[L].has_key(R)
    


    # ----------------------------------------------------------------------------------------------
    def GetNumTrainingWords (self):
        return len (self.current_word_alignments)
            


    # ----------------------------------------------------------------------------------------------
    def GetTrainingWordAlignment (self, given_charseq):
        
        if not self.word_alignments_index_tbl:
            L = len (self.current_word_alignments)
            for i in range(L):
                charseq = self.current_word_alignments[i][0]
                self.word_alignments_index_tbl [charseq] = i
            
        given_charseq = tuple (given_charseq)

        if self.word_alignments_index_tbl.has_key (given_charseq):
            k = self.word_alignments_index_tbl [given_charseq]
            answer = self.current_word_alignments[k][2]
        else:
            answer = []
                
        return answer                    



    # ----------------------------------------------------------------------------------------------
    # Uses: self.production_counts_table_2d
            
    def FindAlignmentSequences (self, 
                                charseq, 
                                phoneseq, 
                                production_score_table = {},
                                verbose = False):
                                
        if verbose: print '\nGiven word:', charseq, phoneseq            
        
        
        if not production_score_table:
            production_score_table = self.production_counts_table_2d
            
            
        production_solutions = []
        work_queue = [(charseq, phoneseq, [])]

            
        while work_queue:
            lhs_remaining, rhs_remaining, derivation = work_queue.pop()
                
            if verbose == 2: print ' examining: %s -> /%s/' \
                %(string.join(lhs_remaining,''), string.join(rhs_remaining,' ')), derivation
                
            if len(lhs_remaining) == 0 and len(rhs_remaining) == 0:
                score = sum (map ((lambda x: x[2]), derivation))
                production_solutions.append ([score, derivation])
                    
            else: # this search could be replaced with a more efficient trie structure
                if len (lhs_remaining) == 0: continue
                lhs_symbol   = lhs_remaining[0]
                rhs_info_tbl = production_score_table.get (lhs_symbol,{})
                    
                for cnt, (rule_rhs, prod_count) in enumerate (rhs_info_tbl.items()):
                    rhs_length = len (rule_rhs)
                    rhs_prefix = tuple (rhs_remaining[:rhs_length])
                    production_applies = rule_rhs == rhs_prefix

                    #if verbose and not production_applies and lhs_symbol == 'c':
                    #    production_string  = '%s -> %s' %(lhs_symbol, rule_rhs)
                    #    print '  consider: %2i. %-6s %s' %(cnt+1, production_applies, production_string)

                    if verbose and production_applies: 
                        production_string  = '%s -> %s' %(lhs_symbol, rule_rhs)
                        print '  mapping: %s' %(production_string)

                    # create a new copy of the derivation sequence and update  
                    # the work queue by adding a new item (the remaining work).
                        
                    if production_applies:
                        updated_derivation = derivation[:]
                        updated_derivation.append ([lhs_symbol, rule_rhs, prod_count]) 
                        new_queue_item = ((lhs_remaining[1:], 
                                           rhs_remaining[rhs_length:], 
                                           updated_derivation))
                        work_queue.append (new_queue_item)

            
        if verbose: print ' solutions:', production_solutions
     
        return production_solutions
    pass
     

    # ----------------------------------------------------------------------------------------------
    def FindNewAllowables (self, given_word_list, given_allowable_prod_tbl):
        

        # ------------------------------------------------------------------------------------------
        def SetProductionCounts (production_counts):
              
            pct = self.production_counts_table_2d = {}

            for (L,R), count in production_counts.items():
                if not pct.has_key(L):
                    pct[L] = {}
                if not pct[L].has_key(R):
                    pct[L][R] = {}
                pct[L][R] = count


        # ------------------------------------------------------------------------------------------
        def ExtractProductionsFromPath (char_seq, phone_seq, best_match_path, verbose=False):
            
            productions = []
            source = ''
            target = []    
                
            for arc in best_match_path:
                match_type = arc[1]
                j,i = phone_to_char_map = arc[2]
                
                # letter and phone line up
                #   case 1. already have an alignment add it to productions and start new one
                #   case 2. new alignment
                    
                if match_type == 'Sub':
                    if source and target:
                        productions.append ((source, tuple(target)))
                        source = char_seq[i]
                        target = [phone_seq[j]]    
                    else:
                        source = char_seq[i]
                        target.append (phone_seq[j])
                
                # there is an extra phone, i.e. 'x' -> /K-S/
                elif match_type == 'Ins':
                    target.append (phone_seq[j])
                        
                # there is an extra letter, i.e. 'aw' -> /A/
                elif match_type == 'Del':        
                    if source and target:
                        productions.append ((source,tuple(target)))
                    source = char_seq[i]
                    target = []
                    productions.append ((source, tuple(target)))
                    source = ''
                    
            if source and target:   
                productions.append ((source,tuple(target)))

            return productions
        pass        


        # ------------------------------------------------------------------------------------------
        def UpdateAllowableProductions (char_seq, phone_seq, dtw_path_list):
                
            new_productions  = []
            productions_list = []

            for onepath in dtw_path_list:
                productions_list.append (ExtractProductionsFromPath (char_seq, phone_seq, onepath, verbose=False))   

                           
            # 1. update self.production_counts_table_2d
            # 2. add to new_productions                
                        
            #print len (productions_list)

            for one_productions_list in productions_list:
                for lhs, rhs in one_productions_list:
                    if not self.HasProduction (lhs, rhs):
                        new_productions.append ([lhs, rhs])
                    self.UpdateOneProduction (lhs, rhs)
                            
            return new_productions
        pass
            
                    
        # Mainline of FindNewAllowables.                          
        # --------------------------------------------------------
        # Fill out the substitution costs table for DTW algorithm.
        # The lhs and rhs are mapped onto strings for DTW.        
            
        DTW = DynamicTimeWarpExperimental.AlignStringLists          # just a shorthand name      
        dtw_substitutions_tbl = {}                                  # substitutions costs for DTW
            
        for prod, prod_count in given_allowable_prod_tbl.items():
            lhs  = string.join (prod[0],'')
            rhs  = string.join (prod[1],'')
            prod = (lhs, rhs) 
            dtw_substitutions_tbl [prod] = 0.0                      # zero cost for known productions
                
        
        # First, try to see if the current pair can be aligned using the known production rules.    
        #                                                                                           
        # Note that we don't have to find all of the possible ways of generating                    
        # the pronunciation from the spelling, so a simplified algorithm would be preferable.       
        #                                                                                           
        # Use dynamic time warping to get an alignment between the spelling and pronunciation.      
        # Warning: The cost table is kind of hacky as an induction bias and is unsatisfactory.      
        #   Deletion and Insertion operations are given a cost twice that of Substitutions (2 vs 1).
        #   Match costs are set very high because the letter and phoneme alphabets are distinct,    
        #   and this guards against accidental overlap.                                             
        #   Once a substitution has been inferred (e.g. a->A), the cost for this is set to zero.    
        # The result from DTW is a list of alignments of minimal cost. This list can have more      
        # than one entry.                                                                           
        #                                                                                           
        # Improvement: make the costs probabilistic and use Viterbi search.                         
        # Initialize dtw_subs table here from the allowables table                                  
 
        triggering_words_list = []                         # words that cause new productions 
        new_productions_list  = []                         # all new productions found        
        alignment_solutions   = []                         # solutions for the given_word_list


        # this initializes self.production_counts_table_2d
        SetProductionCounts (self.production_counts_table_1d)

        for loop_cnt, (charseq, phoneseq) in enumerate (given_word_list):
            #print '%4i %s %s' %(loop_cnt, string.join(charseq,''), string.join(phoneseq,''))

            found_solutions = self.FindAlignmentSequences (charseq, phoneseq, verbose=False)

            if not found_solutions:
                path_cost, path_list = DTW (charseq, 
                                            phoneseq, 
                                            cost_table  = [2,2,1,9999],        # [Ins, Del, Sub, Match]
                                            subst_table = dtw_substitutions_tbl,
                                            verbose     = False)
                        
                new_prods = UpdateAllowableProductions (charseq, phoneseq, path_list)
                   
                for cnt, prod in enumerate (new_prods):
                    item = [loop_cnt+1, cnt+1, charseq, phoneseq] + prod 
                    new_productions_list.append (item)
                triggering_words_list.append (charseq)
                    
                found_solutions = self.FindAlignmentSequences (charseq, phoneseq, verbose=False)
             
            alignment_solutions.append ((charseq, phoneseq, found_solutions))
        pass            
               
        return alignment_solutions, triggering_words_list, new_productions_list
    pass                             
     

    

    # ----------------------------------------------------------------------------------------------
    def RecomputeProductionCounts (self, break_ties = False, explicit_word_set = None):
        

        # ------------------------------------------------------------------------------------------
        def ComputeProductionCounts():
            
            # --------------------------------------------------------
            def UpdateLocalCounts (one_soln, given_production_counts):
                for lhs, rhs, old_prod_score in one_soln: 
                    prod = (lhs, rhs)
                    given_production_counts [prod] = given_production_counts.get(prod,0) + 1
            

            local_production_counts = {}

            for charseq, phoneseq, alignment_solns in self.current_word_alignments:
                if explicit_word_set and charseq not in explicit_word_set: continue
                word = string.join (charseq,'')
                if len (alignment_solns) == 1:
                    UpdateLocalCounts (alignment_solns[0][1], local_production_counts)
     
            return local_production_counts


        # ------------------------------------------------------------------------------------------
        def ScoreSolutions (alignment_solutions, production_counts):
            
            for i, (old_alignment_score, one_alignment) in enumerate (alignment_solutions):
                x1 = map ((lambda x: tuple(x[:2])), one_alignment)    
                x2 = map ((lambda x: production_counts.get(x,0)), x1)    
                new_alignment_score = sum (x2)    
                    
                epsilon_score = 0
                if break_ties:
                    for loop_cnt, (lhs, rhs) in enumerate(x1):
                        if len(rhs) == 0: 
                            epsilon_score += loop_cnt
                    epsilon_score /= 100.0

                alignment_solutions[i][0] = new_alignment_score + epsilon_score
                    
            return map ((lambda x: x[0]), alignment_solutions)
                
                

        # ------------------------------------------------------------------------------------------
        def ReduceSolutions (alignment_solutions, production_counts):
            
            all_scores = ScoreSolutions (alignment_solutions, production_counts)
            max_score  = max (all_scores)
            min_score  = min (all_scores)

            reduced_solutions = []

            for item in alignment_solutions:
                new_alignment_score, one_alignment = item
                if new_alignment_score == max_score:
                    reduced_solutions.append (item)        
                        
            return reduced_solutions
            
                    
              
        # Stage 1. Compute production counts using words with only one alignment.   
        # Stage 2. Use the newly computed production counts to break ties for words 
        #          that have more than one candidate alignment.                     
        #          This will thin out the number of alignments.                     
        # Stage 3. Recompute production counts using words with only one alignment. 

        production_counts = ComputeProductionCounts()

        for i, (charseq, phoneseq, alignment_solns) in enumerate (self.current_word_alignments):
            if explicit_word_set and charseq not in explicit_word_set: continue
            if len (alignment_solns) > 1:
                thinned_solutions = ReduceSolutions (alignment_solns, production_counts)
                self.current_word_alignments[i] = ((charseq, phoneseq, thinned_solutions))
                    
        production_counts = ComputeProductionCounts()


        # Stage 4. Use the new production counts to rescore the surviving alignments.

        for charseq, phoneseq, alignment_solns in self.current_word_alignments:
            if explicit_word_set and charseq not in explicit_word_set: continue
            for j, (old_alignment_score, one_alignment) in enumerate (alignment_solns):
                new_alignment_score = 0
                for k, (lhs, rhs, old_count) in enumerate (one_alignment):
                    prod = (lhs, rhs)
                    one_alignment[k][2]  = production_counts.get (prod,0)
                    new_alignment_score += one_alignment[k][2]
                alignment_solns[j][0] = new_alignment_score    
            

        # return the production counts rather than set an object variable value.

        return production_counts
    pass    
        

                                    

    # --------------------------------------------------------------------------------------------------
    def BatchwiseDiscoverAllowables (self, 
                                     training_word_pronun_list, 
                                     write_progress_files = 0,
                                     progress_output_file = sys.stdout,
                                     verbose = False):

            
        # Set the progress_output_file handle for logging the verbose print statements.
        # If the name is not a string assume it is a file handle, such as sys.stdout.  
            
        if type (progress_output_file) == '':
            log = sys.stdout
        elif type (progress_output_file) == type('string'):
            log = file (progress_output_file, 'w')
        else:        
            log = progress_output_file

        if verbose: log.write ('\nDiscoverLetterProductions for %s words\n\n' %(len(training_word_pronun_list)))


        # Sort the dictionary of training pronunciations.
        
        sorted_key_list, pronunciation_table = DictionaryIO.SortByWordGroups (training_word_pronun_list)
            
        if write_progress_files >= 1:
            DictionaryIO.WriteWordListGrouped   (sorted_key_list, pronunciation_table, 'word_list.txt')
            DictionaryIO.WriteWordListHistogram (sorted_key_list, pronunciation_table, 'word_list.histo')
            
        if verbose: log.write ('Done sorting dictionary\n')
     

        self.production_counts_table_1d = {}    # ocurance count for each letter->phone production, if alignments are unique 
        self.current_word_alignments = []       # one or more alignments are appended for each word, as words are encountered
        all_triggering_words = []               # list of all the words that trigger new letter->phone productions           
        
        loop_cnt = -1   
        for loop_cnt, word_group_key in enumerate (sorted_key_list):
            N = loop_cnt + 1
                
            # define the progress filenames of this iteration
            word_solutions_filename  = Config.solutions_file_prefix   + string.zfill(N,3)
            lts_productions_filename = Config.productions_file_prefix + string.zfill(N,3)
            production_cnts_filename = Config.prod_counts_file_prefix + string.zfill(N,3)

            # get the list of words to work on during this iteration
            working_word_list = pronunciation_table [word_group_key]
            
            if verbose: 
                log.write ('WORDLIST %s' %(working_word_list))
                log.write ('\n%i. Working on word group %s of size %i\n' %(N, str(word_group_key), len(working_word_list)))
                    
            # Find any new productions in the working_word_list and the subset of words that 
            # trigger these new productions.                                                 
                
            found_alignments, triggering_words, new_productions = self.FindNewAllowables (working_word_list, self.production_counts_table_1d)
                
            all_triggering_words         += triggering_words
            self.current_word_alignments += found_alignments
            self.production_counts_table_1d = self.RecomputeProductionCounts (break_ties=True)
            
            if verbose: 
                log.write ('   Num allowable productions:  %i\n'    %(len(self.production_counts_table_1d)))
                log.write ('   Num words needed (new,tot): %i,%i\n' %(len(triggering_words), len(all_triggering_words)))
                
            if write_progress_files >= 2:
                LTS_IO.WriteProductionsSummary (production_cnts_filename, self.production_counts_table_1d)
                LTS_IO.WriteOutProductions     (lts_productions_filename, new_productions)
                LTS_IO.WriteOutSolutions       (word_solutions_filename,  found_alignments)
        pass

        
        # print out the words that triggered new productions
            
        if verbose: 
            log.write ('\nWords leading to new allowable productions:\n')
            
            for cnt, charseq in enumerate (all_triggering_words):
                n = cnt + 1
                word = string.join (charseq,'')    
                log.write ('%4s %3i %s\n' %('', n, word.encode('utf-8') ))
            log.write('\n')
            

        # perform alignment on the entire set

        if verbose: log.write ('Running full alignment\n')
            
        N = loop_cnt + 2
        word_solutions_filename  = Config.solutions_file_prefix   + string.zfill(N,3)
        production_cnts_filename = Config.prod_counts_file_prefix + string.zfill(N,3)
            
        self.production_counts_table_1d = self.RecomputeProductionCounts (break_ties=True)
            
        if write_progress_files >= 1:
            LTS_IO.WriteProductionsSummary (production_cnts_filename, self.production_counts_table_1d)
            LTS_IO.WriteOutSolutions       (word_solutions_filename,  self.current_word_alignments)
            
        if verbose: log.write ('done.\n')
        if type (progress_output_file) == type('string'): log.close()
            



        # -----------------------------------------------------
        # Compute the neglogprob of all letter productions.    
        
        # this is useful for tracing the actions
        # LTS_IO.WriteOutSolutions ('align.txt',  self.current_word_alignments)
            
        productions_neglogprob  = {}
        total_counts_per_letter = {}
             
        #print      
        #print self.production_counts_table_2d
        #print    
            
        enc = codecs.getencoder('utf-8')

        for letter, letter_productions_tbl in self.production_counts_table_2d.items():
            total_prod_counts = sum (letter_productions_tbl.values())
            maxim_prod_counts = max (letter_productions_tbl.values())
            total_counts_per_letter [letter] = total_prod_counts
            productions_neglogprob  [letter] = {}
            
            best_log_prob = abs (log10 (float (maxim_prod_counts) / float (total_prod_counts)))

            """
            try:
                print 'ASC %4s %4i' %(letter, total_prod_counts)
            except UnicodeEncodeError:        
                enc_letter = enc(letter)[0]    
                print 'UTF %4s %4i' %(enc_letter, total_prod_counts)
            print
            """

            for prod_rhs, prod_count in letter_productions_tbl.items():
                neg_log_prob  = abs (log10 (float (prod_count) / float (total_prod_counts)))
                norm_log_prob = neg_log_prob - best_log_prob   
                productions_neglogprob [letter][prod_rhs] = norm_log_prob   
                """
                try:
                    print '%4s %4i %4i %8.4f %s' %(letter, prod_count, total_prod_counts, neg_log_prob, prod_rhs)
                except UnicodeEncodeError:        
                    print '%4s %4i %4i %8.4f %s' %(enc_letter, prod_count, total_prod_counts, neg_log_prob, prod_rhs)
                """     
            #print
        #print
            

        best_alignment_list = []
                
        for loop_cnt, word_group_key in enumerate (sorted_key_list):
            N = loop_cnt + 1
                
            # get the list of words to work on during this iteration
            working_word_list = pronunciation_table [word_group_key]
            
            # print '%3i. WORKING on word group %s of size %i\n' %(N, str(word_group_key), len(working_word_list))
            
            for charseq, phoneseq in working_word_list:
                word  = string.join (charseq,'')
                solns = self.FindAlignmentSequences (charseq, phoneseq, productions_neglogprob, verbose=False)
                
                word_length = float (max (1,len(word)))
                best_score  = 999999999.99
                best_soln   = []    
                    
                for one_soln in solns:
                    soln_score = one_soln[0] / word_length
                    if soln_score < best_score:
                        best_score = soln_score
                        best_soln  = one_soln
                            
                best_alignment_list.append ((best_score, word, best_soln))

                #print 'NumSolns', len(solns), word
                #print    
            #print
        

        """
        # useful for debugging and tracing        
        best_alignment_list.sort()
            
        outfile = codecs.open ('a_word_scores.txt', 'w', 'utf-8')
        for cnt, (score, word, best_soln) in enumerate (best_alignment_list):
            outfile.write ('%6i  %10.8f  %s\n' %(cnt+1, score, word))
        outfile.close()
 
        self.WriteProductionsSummary ('a_letter_prod.txt')
        """
                

        # jmk - ToDo 
        # perform a relaxation step that considers currently impossible productions through DTW suggestions
        # and then scores it with viterbi. This can fix problems with words such as "use" which will get
        # misaligned when the data is small: (u Y, s UW, e Z) when better is (u Y-UW, s Z, e _)

    
        return self.production_counts_table_1d
    pass        
     

# end LTS_Allowables.T
# --------------------

