# LTS_RuleSystemTrain.py
# ======================
# 0.01.001  23-Jan-2006  jmk  Split off from LTS_RuleSystem.
# ---------------------
    
import string, sys
import LTS_RuleSystem

from time import time


# --------------------------------------------------------------------------------------------------
class T (LTS_RuleSystem.T):

    
    # ----------------------------------------------------------------------------------------------
    def _SortProductions (self, given_production_counts_table_1d):
        
        self.production_rules_sorted_list = {}             # maps [lhs] -> sorted (count,rhs) 
        self.production_counts_table_2d   = {}             # maps [lhs][rhs] -> prod counts   

                                                                
        # Reconstruct table_2d from table_1d (which is considered definitive).
        # The table_1d is derived from the word alignment procedure.          
            
        for prod, count in given_production_counts_table_1d.items():
            lhs, rhs = prod
            if not self.production_counts_table_2d.has_key(lhs):
                self.production_counts_table_2d[lhs] = {}
            self.production_counts_table_2d [lhs][rhs] = count
        
        # Create table that maps lhs onto sorted list of rhs productions.
        # The lists are sorted in descending order (by reverse=True).    
            
        for lhs in self.production_counts_table_2d.keys():
            sorted_productions = [(val,key) for (key,val) in self.production_counts_table_2d[lhs].items()]
            sorted_productions.sort (reverse=True)
            self.production_rules_sorted_list [lhs] = sorted_productions
                
    pass
 


    # ----------------------------------------------------------------------------------------------
    def BatchwiseDiscoverRules (self, 
                                max_context_width_to_consider   = 999, 
                                run_with_low_memory_usage       = False,
                                explicit_words_to_use           = None, 
                                verbose                         = False):


        # ------------------------------------------------------------------------------------------
        # Input:    self.production_counts_table_1d                                                 
        #           self.production_rules_sorted_list                                               
        # Output:   self.lts_rule_system                                                            
            
        def InitializeRulesFromProductionCounts():
            
            self.lts_rule_system = {}                           # maps lhs -> learned rule chain          
            self.production_rules_sorted_list = {}              # maps lhs -> sorted list of (counts, rhs)
            self.rule_context_locations  = {}                   # maps [context][rhs] -> set of locations 

            
            if explicit_words_to_use:
                #for i, word in enumerate (explicit_words_to_use):
                #    print 'Exp %4i  %s' %(i+1, string.join(word,''))
                #print        

                prod_counts = self.RecomputeProductionCounts (break_ties=True, explicit_word_set=explicit_words_to_use)
                self._SortProductions (prod_counts)
            else:    
                self._SortProductions (self.production_counts_table_1d)


            lhs_symbol_list = self.production_rules_sorted_list.keys()
            lhs_symbol_list.sort()
                 
            for symbol in lhs_symbol_list:
                rhs_list = self.production_rules_sorted_list [symbol]
                
                if len (rhs_list) > 0:
                    total_prod_count = sum (map ((lambda x: x[0]), rhs_list))
                    prod_count, most_popular_rhs = rhs_list[0]
                    prod_context_info  = ('', symbol, '')
                    default_rule = [prod_context_info, most_popular_rhs, prod_count]
                    self.lts_rule_system [symbol] = [default_rule]
                else:    
                    self.lts_rule_system [symbol] = []
        pass
                   


        # --------------------------------------------------------------------------------------
        def GetCandidateContexts (letter, word_index, letter_index, context_window_width):

            L = context_window_width
                
            letter_seq  = self.current_word_alignments [word_index][0]
            padded_word = '#' + string.join (letter_seq,'') + '#'    
            char_index  = letter_index + 1    
                
            #if verbose: print '  %5i. %2i  %s  %s' %(word_index, char_index, letter, padded_word)
                    
            context_list = []

            for offset in range (-L+1, 1):
                beg     = max (0, char_index + offset)
                end     = max (0, char_index + offset + L)
                left    = padded_word [beg : char_index]
                right   = padded_word [char_index+1 : end]
                context = (left, letter, right)
                        
                if len(left) + len(right) + 1 == context_window_width:        
                    context_list.append (context)
                        
            return context_list
        pass



        # ------------------------------------------------------------------------------------------
        # Comment:  This depends on self.current_word_alignments having been already computed.      
        # Input:    self.current_word_alignments                                                    
        # Output:   self.unexplained_prod_table                                                     

        def ScanForUnexplainedProductions (specified_letter= None, verbose = False):
            
            self.unexplained_prod_table   = {}      # maps lhs -> (word_index, char_index) set  
            self.unexplained_rule_counts  = {}      # maps (lhs,rule) -> integer                
        
            for word_index, item in enumerate (self.current_word_alignments):
                charseq, phoneseq, alignment_list = item
                if len (alignment_list) != 1: continue    
                    
                ### I may get ride of the explicit_words_to_use option
                ### if explicit_words_to_use and charseq not in explicit_words_to_use: continue
                    
                padded_word = ['#','#','#','#'] + list(charseq) + ['#','#','#','#']
                     
                align_score, alignment_data = alignment_list[0]
                    
                # This is a more rigorous way of going about it 
                #prediction_info = self.PredictOneWordPronun (charseq, invert_phone_names=False)
                    
                for char_index, (lhs, rhs, ignore_this) in enumerate (alignment_data):
                    if specified_letter and lhs != specified_letter: continue

                    i  = char_index + 4
                    a1 = padded_word [i-1]
                    a2 = padded_word [i-2] + a1
                    a3 = padded_word [i-3] + a2
                    a4 = padded_word [i-4] + a3
                    b1 = padded_word [i+1]
                    b2 = b1 + padded_word [i+2]
                    b3 = b2 + padded_word [i+3]
                    b4 = b3 + padded_word [i+4]
                          
                    context_list = [(a1,lhs,''), ('',lhs,b1),                                           # W = 2
                                    (a2,lhs,''), (a1,lhs,b1), ('',lhs,b2),                              # W = 3
                                    (a3,lhs,''), (a2,lhs,b1), (a1,lhs,b2), ('',lhs,b3),                 # W = 4
                                    (a4,lhs,''), (a3,lhs,b1), (a2,lhs,b2), (a1,lhs,b3), ('',lhs,b4)]    # W = 5


                    if   max_context_width_to_consider == 1: Upper = 0
                    elif max_context_width_to_consider == 2: Upper = 2
                    elif max_context_width_to_consider == 3: Upper = 5
                    elif max_context_width_to_consider == 4: Upper = 9
                    else:                        Upper = len (context_list)        
                        

                   # ... but direct access is faster.
                   #prediction = prediction_info[1][char_index][1]    
                    prediction = self.lts_rule_system [lhs][0][1]
                    locn = (word_index, char_index)
                        
                    if rhs != prediction:
                        if verbose: 
                            word = string.join (charseq,'')    
                            real_pronun = string.join (rhs,'-')    
                            pred_pronun = string.join (prediction,'-')
                            print '  %5i. %2i %2s -> %-4s %s %s' %(word_index, char_index, lhs, real_pronun, word, pred_pronun), context_list
                                
                        # Update self.unexplained_prod_table 
                        #                                    
                        if not self.unexplained_prod_table.has_key (lhs):
                            self.unexplained_prod_table [lhs] = set()
                        self.unexplained_prod_table [lhs].add (locn)
                            
                        # Update self.unexplained_rule_counts
                        #                                    
                        for context in context_list[:Upper]:
                            #if context[0][:2]  == '##': continue
                            #if context[2][-2:] == '##': continue
                            rule = (context, rhs)
                                
                            if not self.unexplained_rule_counts.has_key(lhs):    
                                self.unexplained_rule_counts [lhs] = {}
                            self.unexplained_rule_counts [lhs][rule] = self.unexplained_rule_counts[lhs].get (rule,0) + 1

                    
                    # Do this out for all bigram contexts    
                    #                                        
                    for context in context_list[:Upper]:
                        if verbose: print '   rule: %i %s -> %s  %s' %(L, context, rhs, locn)
                        
                        #self.context_occurance_counts [context] = self.context_occurance_counts.get (context,0) + 1

                        if not self.rule_context_locations.has_key (context):
                            self.rule_context_locations [context] = {}
                                
                        if not self.rule_context_locations [context].has_key (rhs):
                            self.rule_context_locations [context][rhs] = set()
                                
                        self.rule_context_locations [context][rhs].add (locn)
                
            pass    
                                 

        # ------------------------------------------------------------------------------------------
        # Purpose:  This finds contexts that can explain the currently unexplained productions.     
        # Input:    self.unexplained_prod_table                                                     
        # Output:   self.unexplained_rule_counts                                                    
            
        def FillCandidateContextsOne (given_letter, context_window_width, verbose = False):
            
            # For each letter, run through the location_set of unexplained positions.       
            # A location is a (word_index, char_index) pair into current_word_alignments.   
            # Then for each location, get a list of candidate contexts can can explain the  
            # the production, construct the candidate rule, and count the number of times   
            # each rule appears. A rule is a (context, rhs) pair.                           
                
            L   = context_window_width
            t1  = time()
            lhs = given_letter
                
            location_set = self.unexplained_prod_table [lhs]  
            self.unexplained_rule_counts [lhs] = {} 

 
            for cnt, locn in enumerate (location_set):
                word_index, char_index = locn
                alignment_info = self.current_word_alignments [word_index][2][0][1]
                rhs = alignment_info [char_index][1]
                    
                # build all contexts up to length L
                #                                  
                context_list = []
                for w in range (2, L+1):    
                    context_list.extend (GetCandidateContexts (lhs, word_index, char_index, w))
                    
                # fill out self.unexplained_rule_counts
                #                                      
                for context in context_list:
                    #if self.lts_contexts_used.has_key (context): continue
                    rule = (context, rhs)
                    self.unexplained_rule_counts [lhs][rule] = self.unexplained_rule_counts[lhs].get (rule,0) + 1
            t2 = time()


            if verbose:
                print 'Fill: %4s %6i %6i' %(lhs, len(location_set), len(self.unexplained_rule_counts[lhs]))
            
            return t2-t1    
        pass
                    


        # ------------------------------------------------------------------------------------------
        # This is not completely correct. Need to fix!                                              
        # Input:    self.unexplained_prod_table                                                     
        #           self.unexplained_rule_counts                                                    
        #           self.rule_context_locations                                                     
        # Output:   self.unexplained_prod_table                                                     
        #           self.lts_rule_system                                                            
                 
        def FindBestExplanatoryContexts (verbose = False):
  

            # --------------------------------------------------------------------------------------
            def PerformOneRuleSearch (lhs, candidate_production_benefit):
                        

                # ----------------------------------------------------------------------------------
                def FindOtherMatchingLocations (given_rule):
                    
                    t1 = time()

                    given_context = given_rule[0]
                    given_context_width = len (string.join (given_context,''))
                    if given_context_width < 3: return 0
                      

                    GC = given_context
                    
                    if len(GC[0]) > len(GC[2]):
                        context = (GC[0][1:], GC[1], GC[2])
                    else:        
                        context = (GC[0], GC[1], GC[2][:-1])

                    context_width = len (string.join (context,''))
                        
                        
                    if context_width == given_context_width - 1:     
                        locations = self.rule_context_locations.get (context,{})
                            
                        #rule_list = locations.keys()
                        #locn_size = map ((lambda x:len(x)), locations.values())
                        #if not locations: print '::: %4i %s  %s' %(-1, context, rule_list), locn_size
                            
                        for i, (rhs, location_list) in enumerate (locations.items()):
                            #print '   ', rhs, location_list
                                
                            for j, locn in enumerate (location_list):
                                wi,ci = locn
                                cand_context_list = GetCandidateContexts (GC[1], wi, ci, given_context_width)
                                
                                for cand_context in cand_context_list:
                                    if cand_context == given_context:
                                        #print '%4i %4i %6s' %(i, j, matches), cand_context, locn
                                            
                                        #self.context_occurance_counts [context] = self.context_occurance_counts.get (context,0) + 1
                                        
                                        if not self.rule_context_locations.has_key (cand_context):
                                            self.rule_context_locations [cand_context] = {}
                                        if not self.rule_context_locations [cand_context].has_key (rhs):
                                            self.rule_context_locations [cand_context][rhs] = set()
                                        self.rule_context_locations [cand_context][rhs].add (locn)
                    
                    t2 = time()
                    return t2-t1
                pass        


                # -------------------------
                # Note: I (currently) need to use both self.rule_context_location and self.unexplained_prod_table
                    
                Trace_Char = 'l'

                self.num_searches  += 1
                existing_rule_chain = self.lts_rule_system [lhs]
                num_curr_unsolved   = len (self.unexplained_prod_table.get(lhs,[])) 
                best_rule           = ('','','')
                best_benefit        = 0    
                    
                unexplained_locn_set = self.unexplained_prod_table[lhs]
                unexplained_locn_num = len (unexplained_locn_set)
                scored_candidate_rules = []


                if num_curr_unsolved == 0: 
                    return 0, best_rule
                    
                
                if verbose > 1 and lhs == Trace_Char: 
                    print '\nRefining Rule Chain:', existing_rule_chain
                    print 'Chain Len./Unsolved: %4i %4i' %(len(existing_rule_chain), num_curr_unsolved)
 

                # begin main search loop
                    
                for cnt, (approx_merit, neg_context_width, cand_rule) in enumerate (ranked_rules_by_count):
                    if approx_merit <= best_benefit: break
                        
                    candidate_context, cand_rhs = cand_rule


                    # this is a heuristic for speeding the search          
                    # it skips over productions that didn't work last round
                        
                    prev_benefit = candidate_production_benefit.get (cand_rule,1)
                    if prev_benefit <= 0: continue        
                        
                    # experimentally, this doesn't speed up processing much at all
                    #if self.lts_contexts_used.has_key (candidate_context): continue

                         
                    if not self.rule_context_locations.has_key (candidate_context):
                        self.total_match_time += FindOtherMatchingLocations (cand_rule)
                        #print 'MISSING', cand_rule


                    occurances_table      = self.rule_context_locations.get (candidate_context,{})
                    matching_location_set = occurances_table.get (cand_rhs, set())
                        
                    tmp_cand_set = unexplained_locn_set - matching_location_set
                    tmp_benefit  = unexplained_locn_num - len (tmp_cand_set)

                    if tmp_benefit <= best_benefit: 
                        candidate_production_benefit [cand_rule] = tmp_benefit
                        continue
                        
                    self.num_checks += 1        

                    other_matching_location_set = set()
                    for rhs, locn_set in occurances_table.items():
                        if rhs != cand_rhs: 
                            other_matching_location_set |= locn_set
                        
                   
                    new_cand_set  = tmp_cand_set | other_matching_location_set
                    cand_benefit  = unexplained_locn_num - len (new_cand_set)
                    cand_rule_len = len(candidate_context[0]) + len(candidate_context[2]) + 1   
                           
                    if cand_benefit > best_benefit:
                        scored_candidate_rules.append ((cand_benefit, -cand_rule_len, new_cand_set, cand_rule))
                    best_benefit  = max (best_benefit, cand_benefit)

                    # new addition in an attempt to increase speed: 
                    #self.unexplained_rule_counts [lhs][cand_rule] = cand_benefit
                    candidate_production_benefit [cand_rule] = cand_benefit
                        

                    # -----------------------------------
                    if verbose > 2 and lhs == Trace_Char:                   
                        neg_benefit = len (tmp_cand_set) - len (new_cand_set)
                                                      
                        print '%4i. Candidate context: %4i, %4i, +%4i %4i = %4i %20s -> %s  %s' \
                        %(cnt+1, 
                          approx_merit,
                          len (matching_location_set),  
                          tmp_benefit,
                          neg_benefit,  
                          cand_benefit,  
                          candidate_context, 
                          cand_rhs, 
                          occurances_table.keys())
                pass
                                
                   
                    
                # clean out useless candidate rules from rule_counts_table
                # that is, from self.unexplained_rule_counts              
                """    
                for i in range (len (scored_candidate_rules)):
                    benefit = scored_candidate_rules[i][0]
                    rule    = scored_candidate_rules[i][3]
                    if benefit <= 0: del rule_counts_table [rule]
                    #print 'KILL', rule     
                """


                # sort the scored candidate rules               
                # then add the best rule to self.lts_rule_system
                    
                scored_candidate_rules.sort (reverse=True)
                    
                if scored_candidate_rules:
                    best_benefit  = scored_candidate_rules[0][0]
                    unsolved_set  = scored_candidate_rules[0][2]
                    best_rule     = scored_candidate_rules[0][3]
                    best_rule_mod = [best_rule[0], best_rule[1], best_benefit]
                        
                    rule_counts_table = self.unexplained_rule_counts.get(lhs,{})
                    if rule_counts_table.has_key (best_rule):
                        del rule_counts_table [best_rule]
                        
                    if best_benefit > 0:
                        self.lts_rule_system [lhs].append (best_rule_mod)       # add new rule
                        self.unexplained_prod_table [lhs] = unsolved_set        # update unexplained_prod_table
                        candidate_production_benefit [best_rule] = 0
                        num_curr_unsolved = len (unsolved_set)
                        #self.lts_contexts_used [best_rule[0]] = True
                    else:
                        best_rule = (('','',''), ())
                            

                    if verbose > 2 and lhs == Trace_Char:
                        for i, (benefit, neg_rule_len, new_unsolved_set, rule) in enumerate (scored_candidate_rules):
                            print '%4i. benefit: %4i  %20s' %(i+1, benefit, rule)
                    if verbose > 1:            
                        print 'Checked %i candidate contexts' %(len (scored_candidate_rules))        
                        print 'Unsolved: %4i' %(num_curr_unsolved)
                        
                    
                return num_curr_unsolved, best_rule
            pass
                

            # --------------------------------------------------------------------------------------
            def ReRankCandidates():
                
                def RankCandidates (rule_counts_table):
                    answer = []
                        
                    for rule, count in rule_counts_table.items():
                        context, rhs = rule
                        rule_length  = len(rule[0][0]) + len(rule[0][2]) + 1
                        answer.append ((count, -rule_length, rule))
                            
                    answer.sort (reverse=True)
                    return answer
                        
 
                t1a = time()    
                rule_counts_table     = self.unexplained_rule_counts.get (letter,{})
                ranked_rules_by_count = RankCandidates (rule_counts_table)
                t2a = time()    
                self.total_rank_time += t2a - t1a 
                return ranked_rules_by_count

 

            # ----------------
            # Method mainline.
            # ----------------

            # cand_production_benefit is maintained between calls to PerformOneRuleSearch.
            # It is used to prune out unsuccessfull rules from the previous iteration.    
                
            cand_production_benefit = {}
            total_productions_unsolved = 0
            prev_num_unsolved = [-1,-1]

            lhs_list = self.unexplained_prod_table.keys()
            lhs_list.sort()


            # Run the main loop through all the letters.

            for letter in lhs_list:
                prev_num_unsolved[0] = len (self.unexplained_prod_table.get(letter,[])) 
                prev_num_unsolved[1] = -1
                if prev_num_unsolved[0] == 0: continue    

                if verbose: print 'Working on %s %i' %(letter, prev_num_unsolved[0]),
                    
                ranked_rules_by_count = ReRankCandidates()


                while True:    
                    curr_num_unsolved, new_rule = PerformOneRuleSearch (letter, cand_production_benefit)
                        
                    rule_length = len (string.join (new_rule[0],''))
                    if verbose == 1: print curr_num_unsolved, 
                      
                        
                    # Doing a re-rank every time is guaranteed to find the minimum number of    
                    # covering rules in the fewest number of checks, but the cost of recomputing
                    # the ranked candidate rule list makes the search slower overall.           
                    # self.total_fill_time += FillCandidateContextsOne (letter, 3, verbose = False)
                    # ranked_rules_by_count = ReRankCandidates()
                    

                    # test 1 - exit loop if all productions for this letter are solved  
                        
                    if curr_num_unsolved == 0: break
                   
                    # test 2 - exit loop if the number of unsolved productions hasn't   
                    # changed for two iterations in a row                               
                        
                    elif curr_num_unsolved == prev_num_unsolved[1]: break

                    # test 3 - if the number of unsolved productions hasn't improved    
                    # from the previous loop, recompute and rerank the list of          
                    # candidate rules. This can be necessary when productions that      
                    # were previously solved are now unsolved due to the addition of a  
                    # new rule. Example from Spanish.                                   
                    #   24.  l ->     L / _   [12041]   ex. ("adalid" nil (A D A L I D))
                    #   25.  l ->     _ / l_  [638]     ex. ("acalle" nil (A K A LL E)) 
                    #   26.  l ->    LL / _l  [622]     ex. first 'l' in above word     
                    #   27.  l ->     L / _l# [8]       ex. ("atoll" nil (A T O L))     

                    elif curr_num_unsolved == prev_num_unsolved[0]:
                        if rule_length + 1 <= max_context_width_to_consider:
                            W = rule_length + 1
                        else:
                            W = rule_length  
                                
                        W = max_context_per_letter_scanned [letter]
                        self.total_fill_time += FillCandidateContextsOne (letter, W, verbose = False)
                        ranked_rules_by_count = ReRankCandidates()
                        if verbose: print '-%s-' %(W),    
                        
                    # test 4  - if the current rule context equals the widest contexts  
                    # that have been scaneed for this letter, increase the context      
                    # window by 1 and rescan. (Unless the max is already reached.)      
                        
                    elif rule_length == max_context_per_letter_scanned [letter]:
                        if rule_length + 1 <= max_context_width_to_consider:
                            W = rule_length + 1
                        else:
                            W = rule_length        
                            
                        max_context_per_letter_scanned [letter] = W
                        self.total_fill_time += FillCandidateContextsOne (letter, W, verbose = False)
                        ranked_rules_by_count = ReRankCandidates()
                        if verbose: print '.%s.' %(W),
                                
                         
                    # store current
                    prev_num_unsolved[1] = prev_num_unsolved[0]
                    prev_num_unsolved[0] = curr_num_unsolved
                pass        


                total_productions_unsolved += curr_num_unsolved
                if verbose: print
            if verbose: print

            return total_productions_unsolved
        pass
                


        # ------------------------------------------------------------------------------------------
        def RunOuterSearchLoop (specified_letter=None):
            
                
            ScanForUnexplainedProductions (specified_letter, verbose=False)                   # Step 2
                
            if verbose: 
                print '\nWindow width of: %i' %(1)
                print 'Scan  %8.2f' %(time()-t1)



            # run outer search loop
            prev_num_rules = self.GetNumberOfRules()
            N = 0
                
            while True:
                N += 1
                if verbose: print '\nIteration Num: %i' %(N)
                     
                prev_checks = self.num_checks
                prev_search = self.num_searches    
                t2 = time()    
                num_productions_unsolved = FindBestExplanatoryContexts (verbose=0)      # Step 3
                t3 = time()
                        
                if verbose:
                    print 'Rules %8i'       %(self.GetNumberOfRules())
                    print 'Checks %7i %8i'  %(self.num_checks, self.num_checks - prev_checks)
                    print 'Search %7i %8i'  %(self.num_searches, self.num_searches - prev_search)
                    print 'Find  %8.2f'     %(t3-t2)
                         
                curr_num_rules = self.GetNumberOfRules()
                if curr_num_rules <= prev_num_rules: break
                if num_productions_unsolved == 0: break
                prev_num_rules = curr_num_rules              
            pass


            

        # ----------------
        # Method mainline.
        # ----------------
            
        # These variables are used for measuring the algorithm's performance.

        t1 = time()
        self.num_checks = 0       
        self.num_searches = 0    
        self.total_fill_time = 0
        self.total_rank_time = 0    
        self.total_match_time = 0    

        # Assign the most common production for each letter to be its default lts rule.

        InitializeRulesFromProductionCounts()

        # This is used to control when larger contexts need to be counted
        # because they haven't been precomputed in ScanForUnexplained.   
            
        max_context_per_letter_scanned  = {}    
        letter_list = self.lts_rule_system.keys()

        for lhs in letter_list:
            max_context_per_letter_scanned [lhs] = min (5, max_context_width_to_consider)


        # Run the search loop either scanning one letter at a time or not.

        if run_with_low_memory_usage:
           for lhs in letter_list:
                RunOuterSearchLoop(lhs)
        else:            
            RunOuterSearchLoop()
         

        # Optionally print out various computation times.
            
        if verbose: 
            t6 = time()
            print 'Grand %8.2f\n' %(t6-t1)
            print 'Fill  time: %8.3f' %(self.total_fill_time)
            print 'Match time: %8.3f' %(self.total_match_time)
            print 'Rank  time: %8.3f' %(self.total_rank_time)
            print '\n'    
    pass 


# End class.
# ----------

