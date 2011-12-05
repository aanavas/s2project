# WordSelector.py                                        
#================                                        
# 0.01.002  07-Nov-2005  jmk  Added HappyWithWord method.
# 0.01.001  25-Oct-2005  jmk  Created.                   
# ---------------------                                  


import string, sys
import ConfigPath    
from   Column import column    



# --------------------------------------------------------------------------------------------------
Pivot_Val = 3
    
def OrderAboutPivotValue (val1, val2):
    return abs(val1 - Pivot_Val) - abs(val2 - Pivot_Val)
 


# --------------------------------------------------------------------------------------------------
def NgramsInWord (word):    
    
    unigrams   = {}
    bigrams    = {}
    trigrams   = {}
    quadgrams  = {}
    quintgrams = {}

    for letter in word [1:-1]:
        unigrams[letter] = unigrams.get(letter,0) + 1 
            
    for i in range (len(word)-1):
        ngram = word[i:i+2]
        bigrams[ngram] = bigrams.get(ngram,0) + 1 
            
    for i in range (1, len(word)-1):
        ngram = word[i-1:i+2]
        trigrams[ngram] = trigrams.get(ngram,0) + 1 

    for i in range (len(word)-3):
        ngram = word[i:i+4]
        quadgrams[ngram] = quadgrams.get(ngram,0) + 1

    for i in range (2, len(word)-2):
        ngram = word[i-2:i+3]
        quintgrams[ngram] = quintgrams.get(ngram,0) + 1

    return unigrams, bigrams, trigrams, quadgrams, quintgrams
pass
            



# --------------------------------------------------------------------------------------------------
class T(object):
 
    
    # ----------------------------------------------------------------------------------------------
    def __init__ (self, given_word_list):
        

        # ------------------------------------------------------------------------------------------
        def PrepareForWork():
            
            self.ComputeLetterStats()

            N = len (self.ngram_stats)
                
            for i in range(N):
                self.ngrams_selected.append ({})
                self.ngrams_work_queue.append (self.ngram_stats[i][0][:])   # make a copy of the list
            
            self.word_length_list = self.word_group_tbl.keys()
            self.word_length_list.sort (cmp = OrderAboutPivotValue)    
            self.reverse_word_index = {}
                    
            for i in self.word_length_list:
                self.reverse_word_index[i] = {}
            self.prev_word_length = 0               
        pass       

            
        self.full_word_list      = []
        self.word_freq_table     = {}    
        self.word_id_table       = {}
        self.word_group_tbl      = {}
        self.words_selected_set  = set()
        self.ngrams_selected     = []    
        self.ngrams_work_queue   = []    
        self.ngrams_freq_table   = {}    
        self.num_words_selected  = 0
        self.weighted_word_count = 0
        self.ngram_stats         = []    
        
            
        for word, pronun, count in given_word_list:
            endpointed_word = tuple (['#'] + list(word) + ['#'])
            self.full_word_list.append (endpointed_word)
            self.word_freq_table [endpointed_word] = count
            self.weighted_word_count += count    


        for i, word in enumerate (self.full_word_list):
            L = len(word) - 2
            self.word_id_table[i] = word
            self.word_group_tbl[L] = self.word_group_tbl.get(L,[]) + [i]
                
           
        PrepareForWork()
    pass            



    # ----------------------------------------------------------------------------------------------
    def PercentFinished (self):
        
        word_count = 0
        for word_id in self.words_selected_set:
            word = self.word_id_table [word_id]
            word_count += self.word_freq_table [word]

        words_finished = 100.0 * float (self.num_words_selected) / max (1,len (self.full_word_list))
        words_finished_weighted = 100.0 * float (word_count) / max (1, self.weighted_word_count)
            
        return words_finished_weighted



    # ----------------------------------------------------------------------------------------------
    def GetLetterStats (self):
        return column (self.ngram_stats)

        

    # ----------------------------------------------------------------------------------------------
    def ComputeLetterStats (self):
        
        self.ngram_stats = []
        unigram_stats    = {}
        bigram_stats     = {}
        trigram_stats    = {}
        quadgram_stats   = {}
        quintgram_stats  = {}
                       

        for word in self.full_word_list:
            word_weight = self.word_freq_table.get(word,1)

            for letter in word [1:-1]:
                unigram_stats [letter] = unigram_stats.get(letter,0) + word_weight
                    
            for i in range (len(word)-1):
                ngram = word[i:i+2]
                #assert len(ngram) == 2
                bigram_stats [ngram] = bigram_stats.get(ngram,0) + word_weight 
                    
            for i in range (1, len(word)-1):
                ngram = word[i-1:i+2]
                #assert len(ngram) == 3
                trigram_stats [ngram] = trigram_stats.get(ngram,0) + word_weight 
                    
            for i in range (len(word)-3):
                ngram = word[i:i+4]
                #assert len(ngram) == 4
                quadgram_stats [ngram] = quadgram_stats.get(ngram,0) + word_weight 
                    
            for i in range (2, len(word)-2):
                ngram = word[i-2:i+3]
                #assert len(ngram) == 5
                quintgram_stats [ngram] = quintgram_stats.get(ngram,0) + word_weight 
 

        self.ngram_stats.append (['', unigram_stats])
        self.ngram_stats.append (['', bigram_stats])
        self.ngram_stats.append (['', trigram_stats])
        self.ngram_stats.append (['', quadgram_stats])
        self.ngram_stats.append (['', quintgram_stats])


        for i in range (len (self.ngram_stats)):
            stats = self.ngram_stats[i][1]
            temp = [(count, symbol) for (symbol, count) in stats.items()]
            temp.sort (reverse=False)    
            self.ngram_stats[i][0] = temp
                
            for count, ngram in temp:
                self.ngrams_freq_table [ngram] = count

    pass    
        



    # ----------------------------------------------------------------------------------------------
    def UpdateReverseIndex (self, for_word_length):
        
        L = for_word_length

        self.reverse_word_index[L] = {}
                                 
        for word_id in self.word_group_tbl.get (L,[]):
            word = self.word_id_table [word_id]
            ngrams_by_length = NgramsInWord (word)
                
            for ngram_table in ngrams_by_length:
                for ngram in ngram_table.keys():
                    if self.reverse_word_index[L].has_key (ngram):
                        self.reverse_word_index[L][ngram].add (word_id)
                    else:    
                        self.reverse_word_index[L][ngram] = set ([word_id])
    
        


    # ---------------------------------------------------------------------------------------------
    def ScoreWord (self, given_word):

        ngrams_by_length = NgramsInWord (given_word)
        tot_word_score   = 0
            
        for i, ngram_table in enumerate (ngrams_by_length):
            for ngram, occurances_in_word in ngram_table.items():
                num_ngrams_selected_already = self.ngrams_selected[i].get (ngram,0)
                ngram_freq = self.ngrams_freq_table.get(ngram,0)
                    
                if num_ngrams_selected_already == 0:
                    tot_word_score += ngram_freq  # * occurances_in_word

                word = string.join (given_word,'')
                #print '%12s %4i %4i %4i %6i %8i %s' %(word, i+1, occurances_in_word, num_ngrams_selected_already, ngram_freq, tot_word_score, ngram)

        word_length = len(given_word) - 2               # because it has already been endpointed
        ave_word_score = float(tot_word_score) / word_length
            
        #print '%8.4f' %(ave_word_score)
            
        return ave_word_score
            


    # ---------------------------------------------------------------------------------------------
    def HappyWithWord (self, given_word):
       
        endpointed_word  = tuple (['#'] + list(given_word) + ['#'])
        ngrams_by_length = NgramsInWord (endpointed_word)
        self.prev_word_length = 0    
            
        try:
            for i, ngram_table in enumerate (ngrams_by_length):
                for ngram, count in ngram_table.items():
                    self.ngrams_selected[i][ngram] = self.ngrams_selected[i].get (ngram,0) + count


            for i, queue in enumerate (self.ngrams_work_queue):
                while queue:    
                    ngram = queue[-1][1]
                    N = len(ngram) - 1 
                    already_covered_ngram = self.ngrams_selected[N].get(ngram,0)
                    if already_covered_ngram:
                        queue.pop() 
                    else:        
                        break
 
        except IndexError:
            pass
                

         
    # ---------------------------------------------------------------------------------------------
    def SelectOneWord (self, word_as_charseq = False, verbose=False):
            
        for N, queue in enumerate (self.ngrams_work_queue):
            while queue:    
                desired_ngram = queue[-1][1]
                ngram_length  = len (desired_ngram)  
                    
                if verbose:
                    print 'hunting for: %3s %5i' %(string.join(desired_ngram,'')), 
                    for q in self.ngrams_work_queue: print '%5i' %(len(q)),
                        
                     
                for L in self.word_length_list:
                    if L < self.prev_word_length: continue 
                    #print '  in words of length:', L, 
                        
                    if len (self.reverse_word_index[L]) == 0:
                        self.UpdateReverseIndex(L)
                        #print self.reverse_word_index.keys()    
                        if verbose > 1: print 'Updating Reverse Index', L, ngram_length

                    matching_word_set = self.reverse_word_index[L].get (desired_ngram, [])
                        
                    for id_num in matching_word_set:
                        if verbose:
                            print '%4i' %(len(matching_word_set)),


                        if id_num not in self.words_selected_set:
                            selected_word = self.word_id_table [id_num]
                            self.words_selected_set.add (id_num)
                            matching_word_set.remove (id_num)
                            self.prev_word_length = L
                            self.num_words_selected += 1    
                            ngram_score = self.ngram_stats[N][1][desired_ngram]
                            
                            if word_as_charseq:
                                word = selected_word[1:-1]
                            else:        
                                word = string.join (selected_word[1:-1], '')

                            return word, desired_ngram, ngram_score
                        
                            
                queue.pop()
                self.prev_word_length = 0    
                if verbose: print 'END'
                
        raise IndexError, 'No more words'
    pass
        


        
    # ----------------------------------------------------------------------------------------------
    def SelectOneWord_Ver2 (self, verbose=False):
        

        # ------------------------------------------------------------------------------------------
        def SelectFromWordSet (given_word_id_set, verbose=False):
            
            best_id    = -1
            best_score = 0
                
            if verbose: print 'Word set size', len(given_word_id_set)
                
            for i, id_num in enumerate (given_word_id_set):
                if id_num in self.words_selected_set: continue
                cand_word  = self.word_id_table [id_num]
                cand_score = self.ScoreWord (cand_word)
                    
                if cand_score > best_score:
                    best_score = cand_score
                    best_id = id_num    

                if verbose: print '%4i %4i %8.2f %8.2f %s' %(i, id_num, cand_score, best_score, string.join(cand_word,''))
            if verbose: print
                  
            return best_id
        pass



        high_score = 0
        high_index = 0
        high_queue = []    
                    
        for i, queue in enumerate (self.ngrams_work_queue):
            if not queue: continue
            score = queue[-1][0]
            if score > high_score:
                high_score = score
                high_queue = queue
                high_index = i


        if high_queue:    
            queue = high_queue
            desired_ngram = queue[-1][1]
                
            if verbose:
                print 'hunting for: %5s %2i %5i' \
                    %(string.join(desired_ngram,''), high_index+1, len(queue)),
                    
            for L in self.word_length_list:
                if L < self.prev_word_length: continue 
                    
                if len (self.reverse_word_index[L]) == 0:
                    self.UpdateReverseIndex(L)
                    if verbose > 1: print 'Updating Reverse Index', L, len(desired_ngram)

                matching_word_set = self.reverse_word_index[L].get (desired_ngram, [])
                    
                if matching_word_set:
                    if verbose: print '%4i' %(len(matching_word_set)),

                    id_num = SelectFromWordSet (matching_word_set)
                    
                    selected_word = self.word_id_table [id_num]
                    self.words_selected_set.add (id_num)
                    matching_word_set.remove (id_num)
                    self.prev_word_length = L
                        
                    N = len(desired_ngram) - 1
                    ngram_score = self.ngram_stats[N][1][desired_ngram]

                    return selected_word[1:-1], desired_ngram, ngram_score
        
            # handle case where no word was found to match the desired ngram
            queue.pop()
            self.prev_word_length = 0    
            if verbose: print 'END'
        
        if verbose: print '\n'
            
        raise IndexError, 'No more words'
    pass



    # ----------------------------------------------------------------------------------------------
    def SelectOneWord_Ver4 (self, given_ngram_list = [], verbose=False):
        
        curr_work_queue = []
        
        curr_work_queue.append (self.ngrams_work_queue[0])
            
        for i in range (1, len(self.ngrams_work_queue)):
            curr_work_queue.append({})
                

        all_letters = self.ngram_stats[0][1].keys()
        
        for given_ngram in given_ngram_list:
            N = len (given_ngram)
                
            for ltr in all_letters:
                ngram1 = tuple ([ltr] + list(given_ngram))
                ngram2 = tuple (list(given_ngram) + [ltr])
                    
                for ngram in [ngram1, ngram2]:
                    if not self.ngrams_selected[N].get(ngram,0):
                        score = self.ngram_stats[N][1].get(ngram,0)
                        if score > 0:    
                            curr_work_queue[N][ngram] = score    
                

        for i in range (1, len(curr_work_queue)):
            temp = [(score, symbol) for (symbol, score) in curr_work_queue[i].items()]
            temp.sort (reverse=False)    
            curr_work_queue[i] = temp    
 

        """
        print
        for i, Q in enumerate (curr_work_queue):
            print '%2i %4i %s' %(i+1, len(Q), Q)
        """ 

        return self.SelectOneWord_Ver3 (curr_work_queue, verbose=verbose)        
    pass
        

        

    # ----------------------------------------------------------------------------------------------
    def SelectOneWord_Ver3 (self, given_work_queue = [], verbose=False):
        

        # ------------------------------------------------------------------------------------------
        def SelectFromWordSet (given_word_id_set, verbose=False):
            
            best_id    = -1
            best_score = 0
                
            if verbose: print 'Word set size', len(given_word_id_set)
                
            for i, id_num in enumerate (given_word_id_set):
                if id_num in self.words_selected_set: continue
                cand_word  = self.word_id_table [id_num]
                cand_score = self.ScoreWord (cand_word)
                    
                if cand_score > best_score:
                    best_score = cand_score
                    best_id = id_num    

                #if verbose: print '%4i %4i %8.2f %8.2f %s' %(i, id_num, cand_score, best_score, string.join(cand_word,''))
                  
            return best_id, best_score
        pass


        if not given_work_queue:
            use_ngrams_work_queue = self.ngrams_work_queue
        else:        
            use_ngrams_work_queue = given_work_queue

        high_score = 0
        high_index = 0
        high_queue = []    
                    
        for i, queue in enumerate (use_ngrams_work_queue):
            if not queue: continue
            score = queue[-1][0]
            if score > high_score:
                high_score = score
                high_queue = queue
                high_index = i


        if high_queue:    
            queue = high_queue
            desired_ngram = queue[-1][1]
                
            if verbose:
                print 'hunting for: %5s %2i %5i |' %(string.join(desired_ngram,''), high_index+1, high_score), 
                for q in use_ngrams_work_queue: 
                    try:
                        print '%5i' %(q[-1][0]),
                    except IndexError,msg:
                        print '%5i' %(0),
                print '|',
                for q in use_ngrams_work_queue: 
                    print '%5i' %(len(q)),
                print '|',
              
                 
            total_words_seen = 0
            best_word_score  = 0
            best_word_idnum  = 0    
            best_word_length = 1    
            best_word_set    = set()
                        
            SIZE_LIMIT = 100

            for L in self.word_length_list:
                if len (self.reverse_word_index[L]) == 0:
                    self.UpdateReverseIndex(L)
                    if verbose > 1: print 'Updating Reverse Index', L, len(desired_ngram)

                matching_word_set = self.reverse_word_index[L].get (desired_ngram, [])
                    
                if matching_word_set and total_words_seen < SIZE_LIMIT:
                    #if verbose: print '%4i' %(len(matching_word_set)),
                        
                    total_words_seen += len(matching_word_set)
                    id_num, score = SelectFromWordSet (matching_word_set, verbose=False)
                    selected_word = self.word_id_table [id_num]
                        
                    if score > best_word_score:
                        best_word_score  = score
                        best_word_idnum  = id_num    
                        best_word_length = L
                        best_word_set    = matching_word_set


            self.words_selected_set.add (best_word_idnum)
            best_word_set.remove (best_word_idnum)
            self.prev_word_length = best_word_length
                
            N = len (desired_ngram) - 1
            ngram_score = self.ngram_stats[N][1][desired_ngram]
                
            #best_word = string.join (self.word_id_table [best_word_idnum],'')
            #print 'BEST', best_word_idnum, best_word_score, best_word
            
            selected_word = self.word_id_table [best_word_idnum]

            return selected_word[1:-1], desired_ngram, ngram_score
 
            
        if verbose: print '\n'
            
        raise IndexError, 'No more words'
    pass


  
# end WordSelector.T
# ------------------
    


# --------------------------------------------------------------------------------------------------
def SortWordListByNgramCoverage (lts_learner, given_word_pronun_list, phone_inversion_table = {}):

    
    # ----------------------------------------------------------------------------------------------
    def WordString (word_id):
        
        if word_id < 0 or word_id > len (given_word_pronun_list) - 1:
            return ''
        else:
            return string.join (given_word_pronun_list [word_id][0],'')
            

        
    # ----------------------------------------------------------------------------------------------
    def CountRuleOccurances (word_pronun_list):
        
        rule_count_table = {}
        rule_wordid_sets = {}

        for i, (charseq, pronun) in enumerate (word_pronun_list):
            predicted_pronun, predicted_alignment = lts_learner.PredictOneWordPronun (charseq)
        
            for lhs, rhs, production_list in predicted_alignment:
                if production_list:
                    rule_rank = production_list[0][2]
                    rule_code = (lhs, rule_rank)
                    rule_count_table [rule_code] = rule_count_table.get (rule_code,0) + 1
                        
                    if not rule_wordid_sets.has_key (rule_code):
                        rule_wordid_sets [rule_code] = set()
                    rule_wordid_sets [rule_code].add(i) 
            

        rules_by_lhs = {}
                         
        for rule_code, rule_count in rule_count_table.items():
            lhs, rule_rank = rule_code
            item = (rule_count, rule_code)
            rules_by_lhs[lhs] = rules_by_lhs.get(lhs,[]) + [item]
            rules_by_lhs[lhs].sort (reverse=True)
                
        key_list = rules_by_lhs.keys()
        key_list.sort()
            
        for key in key_list:
            print '%s %s' %(key, rules_by_lhs[key])        
        print        
        

        return rule_count_table, rule_wordid_sets, rules_by_lhs
    pass
            

    # ----------------------------------------------------------------------------------------------
    def UpdateWordIdSets (word_id, rule_set):
        for rule_code in rule_set:
            rule_word_id_sets [rule_code].discard (word_id)
                


    # ----------------------------------------------------------------------------------------------
    def FindBestWordInSet (given_word_set, rules_not_covered, verbose=False):


        # ----------------------------------------------
        def PartialOrderingViolationPenalty (word_rule_counts): 

            temp_rule_count = {}
            total_penalty   = 0

            for rule, word_count in word_rule_counts.items():
                temp_rule_count [rule] = selected_words_rule_count_tbl.get(rule,0) + word_count
                    

            for rule, word_count in word_rule_counts.items():
                for compare_count, compare_rule in sorted_rule_list:
                    if rule[0] == compare_rule[0]:
                        if rule_count_table [rule] < rule_count_table [compare_rule] and \
                            temp_rule_count [rule] >= temp_rule_count.get(compare_rule,0):
                            #print '  ordering violation with rule %6i %6i %s %s %6i' \
                            #    %(count, rule_count_table [compare_rule], compare_rule, rule, rule_count_table[rule])
                            total_penalty += rule_count_table [rule] - rule_count_table [compare_rule]
                       
            #if total_penalty: print 'Penalty', total_penalty
            return total_penalty
        pass
            

        best_score = -9999999999.999
        best_index = -1
        best_rules = {}
        best_rule_counts = {}

        for i, word_id in enumerate (given_word_set):
            charseq = given_word_pronun_list [word_id][0]
            predicted_pronun, predicted_alignment = lts_learner.PredictOneWordPronun (charseq)
        
            cand_score = 0
            cand_rules = set()
            cand_rule_counts = {}    
                
            for lhs, rhs, production_list in predicted_alignment:
                if production_list:
                    rule_rank = production_list[0][2]
                    rule_code = (lhs, rule_rank)
                    cand_rule_counts [rule_code] = cand_rule_counts.get(rule_code,0) + 1
                   
                    if not rule_code in cand_rules and rule_code in rules_not_covered:
                        rule_count = rule_count_table [rule_code]
                        cand_score += rule_count
                        cand_rules.add (rule_code)
                            
            cand_score += PartialOrderingViolationPenalty (cand_rule_counts)
            cand_score  = float(cand_score) / len(charseq)      
                        
            if cand_score > best_score: 
                best_score = cand_score
                best_rules = cand_rules    
                best_index = word_id
                best_rule_counts = cand_rule_counts    
                
            if verbose:        
                word = string.join (charseq,'')
                print '  %4i %6i %6i %8.2f %8.2f  %s' %(i+1, word_id, best_index, cand_score, best_score, word)


        if best_index < 0: 
            print 'Error: no best index'
            sys.exit()
                

        for rule in best_rules:
            rules_not_covered.discard(rule) # Note the modification
            
        return best_index, best_score, best_rules, best_rule_counts
    pass




    # ----------------------------------------------------------------------------------------------
    def FindCoverageWordList (sorted_rule_list):
        

        # ------------------------------------------------------------------------------------------
        def FindOneWord (given_rule_list, rules_not_covered, test_size_threshold = 1):
                
            prev_word_set   = set()
            cand_word_set   = set()
            local_rule_list = given_rule_list[:]
           #local_rule_list.reverse()

            for i, (count, rule) in enumerate (local_rule_list):
                if rule not in rules_not_covered: continue
                    
                if not cand_word_set:
                    cand_word_set = rule_word_id_sets [rule]
                else:
                    cand_word_set = cand_word_set.intersection (rule_word_id_sets[rule])
                
                
                if cand_word_set: 
                    prev_word_set = cand_word_set           # save the last non-empty set
                    if len(cand_word_set) <= test_size_threshold: break
                else:        
                    cand_word_set = prev_word_set           # restore the candidate set to be non-empty
                
                # alternate halt strategry that is
                # not as effective as the above   
                # if not cand_word_set: break     
                # prev_word_set = cand_word_set   

                
            best_id, best_score, best_rules, rule_counts = FindBestWordInSet (prev_word_set, rules_not_covered, verbose=False)
            best_word     = string.join (given_word_pronun_list[best_id][0],'')
            cand_word_set = rule_word_id_sets[rule]
                
            n = len (sorted_word_id_list) + len (best_word_id_list) + 1

            print 'Word %6i %5i %8.2f %4i %4i  %s' %(n, len(best_word), best_score, len(best_rules), len(rules_not_covered), best_word), best_rules
        
            return best_id, rule_counts
        pass        
        #---
           
            
        
        
        Set_Size_Threshold = 100
          
        # old
        # non_covered_rules = set (column (filter ((lambda x: len(x[1]) > 0), rule_word_id_sets.items())))
            
        non_covered_rules = set()
        for count, rule in sorted_rule_list:
            rule_lhs, rule_rhs_index = rule
            if rule_rhs_index == 1 and rule_word_id_sets[rule]:
                non_covered_rules.add (rule)


        best_word_id_set  = set()
        best_word_id_list = []
            
            
        # pass 1
        
        loop_count = 0
        num_reinsertions = 0    
            
                
        while non_covered_rules:    
            loop_count += 1
            if loop_count >= 510: return best_word_id_list      # jmk!!!
                
            print '%6i. Searching for %i rules among %i ...' %(loop_count, len(non_covered_rules), len(sorted_rule_list))
                
            
            # resort the rules
            sorted_rule_list = [(count, rule) for (rule, count) in rule_count_table.items()]
            sorted_rule_list.sort (reverse=True)

            j = 0
            for count, rule in sorted_rule_list:
                if rule in non_covered_rules:
                    j += 1
                    print '%6i looking %6i %s' %(j, count, rule)    
            print
            

                    
            best_word_id, rules_covered = FindOneWord (sorted_rule_list, non_covered_rules, Set_Size_Threshold)
                
            best_word_id_set.add (best_word_id)
            best_word_id_list.append (best_word_id)    
            UpdateWordIdSets (best_word_id, rules_covered.keys())
                

            for rule, count in rules_covered.items():    
                selected_words_rule_count_tbl [rule] = selected_words_rule_count_tbl.get(rule,0) + count
                  

            word_charseq = given_word_pronun_list [best_word_id][0]
            word_charset = set (word_charseq)    
            word  = string.join (word_charseq,'')


            for lhs in word_charset:
                rule_chain = rule_count_lhs_table.get(lhs,[])
                    
                for i in range (1,len(rule_chain)):
                    this_rule_total, this_rule = rule_chain[i]
                    prev_rule_total, prev_rule = rule_chain[i-1]
                    this_rule_count = selected_words_rule_count_tbl.get (this_rule,0)
                    prev_rule_count = selected_words_rule_count_tbl.get (prev_rule,0)
                    
                    print 'here %2s %4i %6i %8s %12s %-2i %6i' \
                        %(lhs, i, prev_rule_count, prev_rule, this_rule, this_rule_count, this_rule_total),
                         
                    if this_rule_count == 0:
                        if this_rule not in non_covered_rules:
                            non_covered_rules.add (this_rule)
                            print '  adding this', this_rule,
                                
                            if prev_rule_count <= 1:
                                non_covered_rules.add (prev_rule)
                                rule_count_table [prev_rule] = this_rule_total + 1   
                                print '  adding prev', prev_rule,
                        print
                        break        
                        
                    elif prev_rule_count <= this_rule_count and prev_rule not in non_covered_rules:
                        non_covered_rules.add (prev_rule)
                        rule_count_table [prev_rule] = this_rule_total + 1   
                        print '  adding prev', prev_rule    
                        break    
                    else:
                        print
                         
            print

            """
            for word_rule, word_count in rules_covered.items():
                rule_lhs, rule_rank = word_rule
                rule_chain = rule_count_lhs_table [rule_lhs]
                N = len (rule_chain)    
                next_rule = ''

                for i, (occurance_count, rule) in enumerate (rule_chain):
                    if rule == word_rule:
                        if i+1 < N:
                            next_rule = rule_chain[i+1][1]
                            break
                                
                rule_already_wanted = next_rule in non_covered_rules
                    
                if next_rule and not rule_already_wanted:
                    non_covered_rules.add (word_rule)
                    non_covered_rules.add (next_rule)
                        
                this_word_count = selected_words_rule_count_tbl.get (word_rule,0)
                next_word_count = selected_words_rule_count_tbl.get (next_rule,0)

                print 'here %4i %s %6s %s %6i %6i %s' \
                    %(len(non_covered_rules), rule, rule_already_wanted, next_rule, this_word_count, next_word_count, word)
            """        

           
            """
            for rule in rules_covered.keys():    
                selected_rule_count = selected_words_rule_count_tbl [rule]
                #print '%6i %6i %2i %s' %(rule_count_table[rule], selected_rule_count, count, rule)
                
                # this is inefficient!
                for compare_count, compare_rule in sorted_rule_list:
                    if rule[0] == compare_rule[0]:
                        if rule_count_table [rule] <                \
                          rule_count_table [compare_rule]           \
                        and                                         \
                           selected_words_rule_count_tbl [rule] >=  \
                           selected_words_rule_count_tbl.get(compare_rule,0):
                            num_reinsertions += 1
                            non_covered_rules.add (compare_rule)
                            #print '  re-adding rule %6i %6i %s' %(count, rule_count_table [compare_rule], compare_rule)
            """
                
        pass 
                
        print 'Num reinsertions', num_reinsertions
        return best_word_id_list
        
        # Note: pass 2 may not work with this revised algorithm, so skip
            


        # pass 2

        non_covered_rules   = set (column (filter ((lambda x: len(x[1]) > 0), rule_word_id_sets.items())))
        total_letter_count  = 0 
        total_rules_covered = set()    
        accumulated_score   = 1.0    
        new_word_id_list    = []

        while best_word_id_set:
            word_id, word_score, word_rules, rule_counts = FindBestWordInSet (best_word_id_set, non_covered_rules) 
            best_word_id_set.discard (word_id)
            new_word_id_list.append  (word_id)    
            UpdateWordIdSets (word_id, word_rules)
                
            list_size = len (new_word_id_list)
            entry = given_word_pronun_list [word_id]    
            word  = string.join (entry[0],'')
            total_letter_count  += len(word)    
            total_rules_covered |= word_rules
            current_merit = sum (map ((lambda x: rule_count_table[x]), total_rules_covered))
            current_score = 1.0 - float(current_merit) / maximum_merit    
            accumulated_score += current_score * len(word)
            
            print '%4i %5i %8.2f %4i %4i %8i %8.3f %8.3f %s' \
                %(list_size, total_letter_count, word_score, len(word_rules), len(total_rules_covered), current_merit, current_score, accumulated_score, word)
                    
            if not non_covered_rules: break
        print


        return new_word_id_list
    pass 
        



    # ---------------------------------
    rule_count_table, rule_word_id_sets, rule_count_lhs_table = CountRuleOccurances (given_word_pronun_list)
        
    maximum_merit = sum (rule_count_table.values())    

    sorted_rule_list = [(count, rule) for (rule, count) in rule_count_table.items()]
    sorted_rule_list.sort (reverse=True)

    
    for i, (count, rule) in enumerate (sorted_rule_list):
        print '%4i. %6i %2s -> %i' %(i+1, count, rule[0], rule[1])
    print
    

    selected_words_rule_count_tbl = {}
    sorted_word_id_list = []
        
    while len (sorted_word_id_list) < len (given_word_pronun_list):
        additional_word_list = FindCoverageWordList (sorted_rule_list)
        if not additional_word_list: break
        sorted_word_id_list.extend (additional_word_list)
        if len(sorted_word_id_list) > 5: break    # jmk!!! added a temporary short-circuit 
              
         
    for i, word_id in enumerate(sorted_word_id_list):
        print '%4i. %s' %(i+1, WordString (word_id))
    print


    unique_word_id_set  = set()
    unique_word_id_list = []
        
    for word_id in sorted_word_id_list:
        if word_id not in unique_word_id_set:
            unique_word_id_list.append (word_id)
            unique_word_id_set.add     (word_id)    

    answer = map ((lambda x: given_word_pronun_list[x]), unique_word_id_list)
        
    return answer
pass




# ==============
# Mainline code.
# ==============
    
if __name__ == '__main__':
    import sys
    import DictionaryIO    
            
    lexicon_pathname = sys.argv[1]

    word_list = DictionaryIO.ReadLexiconFileWithCounts (lexicon_pathname, words_only=False)
    selector  = T (word_list)
    loop_cnt  = 0    

    try:
        while True:
            loop_cnt += 1    
            charseq, ngram, score = selector.SelectOneWord(False)
            selector.HappyWithWord (charseq)
            print '%4i %6i %3s %s' %(loop_cnt, score, string.join(ngram,''), string.join(charseq,''))
    except IndexError, msg:
        print msg

        

