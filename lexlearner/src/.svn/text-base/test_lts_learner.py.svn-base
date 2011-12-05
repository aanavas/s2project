# test_lts_learner.py                                           
# ===================                                           
# 0.02.002  24-May-2007  jmk  Added predict_* flags.            
# 0.02.001  14-Mar-2007  jmk  Revised to support utf-8.         
# 0.01.003  11-Nov-2005  jmk  Adeed lts_learner_config.py       
# 0.01.002  07-Nov-2005  jmk  Added three command line flags.   
# 0.01.001  26-Oct-2005  jmk  Created.                          
# ---------------------                                         
 
import getopt, os
import string, sys
import random    
import time
    
import DictionaryIO    
import PronunciationOracle 
import WordSelector       
import LTS_IO
import LTS_RuleSystemTrain as LTS

from Column import column
    

# --------------------------------------------------------------------------------------------------
# Bug. This only works when initialized with alignments under the condition that the phone names    
#      have been disguised (because the prediction will be in disguised phones and the reference    
#      in transparent phones.                                                                       
        
class Measurer (object):
    

    # ----------------------------------------------------------------------------------------------
    def __init__ (self):
        self.word_alignments_list = []



    # ----------------------------------------------------------------------------------------------
    def InitWithAlignments (self, word_alignment_pathname):
        
        import LTS_Allowables
            
        lts_learner = LTS_Allowables.T()
        state_info  = lts_learner.LoadStateInfoAlignment (word_alignment_pathname)
        self.word_alignments_list = state_info[1]
        self.name_inversion_table = lts_learner.GetPhoneNameInvTable()
  


    # ----------------------------------------------------------------------------------------------
    def GetWordPronunList (self):
        
        answer = []
        for charseq, disguised_phone_seq, alignment in self.word_alignments_list:
            phoneseq = map ((lambda x: self.name_inversion_table.get(x,x)), disguised_phone_seq)
            answer.append ((charseq, phoneseq, 1))
                
            print charseq, alignment[0][1]
            print disguised_phone_seq, phoneseq        
            print sorted (self.name_inversion_table)

            for item in alignment[0][1]:
                print item[0], item[1]
                print '  ', item[0], self.name_inversion_table [item[1][0]]
                 
            sys.exit()        
        return answer
            

    # ----------------------------------------------------------------------------------------------
    def GetWordAlignmentList (self):
        
        answer = []
            
        for charseq, disguised_phone_seq, alignment in self.word_alignments_list:
            one_alignment = []
                
            for item in alignment[0][1]:
                if len(item[1]) > 0:    
                    rhs = self.name_inversion_table.get (item[1][0])
                else:
                    rhs = '_'        
                lhs = item[0]
                one_alignment.append ((lhs, rhs))
            answer.append (one_alignment)
                
        return answer


    # ----------------------------------------------------------------------------------------------
    def WriteWagonTrainingData (self, out_pathname):
        
        aligned_data = self.GetWordAlignmentList()
            
        outfile = file (out_pathname,'w')

        for one_alignment in aligned_data:
            L = len (one_alignment)
                
            for i in range(L):
                lhs, rhs = one_alignment[i]
                outfile.write ('%-3s ' %(rhs))
                    
                for j in range (i-3, i+2):
                    if j < 0 or j >= L:
                        lhs = '#'
                    else:
                        lhs = one_alignment[j][0]
                    outfile.write('%2s ' %(lhs))
                outfile.write('\n')
        outfile.close()


 
    # ----------------------------------------------------------------------------------------------
    def MeasurePredictionAccuracy (self, lts_learner, given_lts_rules=None, verbose=True):

        # -----------------------------------------------------------------------------------------
        def CompareAlignments (ref_alignment_list, hyp_alignment):
            
            NIT = self.name_inversion_table

            characters_in_word = len (hyp_alignment)
            characters_correct = 0
                
            if len (ref_alignment_list) > 0:
                score, ref_alignment = ref_alignment_list[0]
                
                for i in range (len (ref_alignment)):
                    ref_letter = ref_alignment[i][0]
                    hyp_letter = hyp_alignment[i][0]
                    ref_phones = tuple (map ((lambda x: NIT.get(x,x)), ref_alignment[i][1]))
                    hyp_phones = hyp_alignment[i][1]
                    assert ref_letter == hyp_letter
                    if ref_phones == hyp_phones:
                        characters_correct += 1
                        
            return characters_correct, characters_in_word
        pass        


        total_words_correct   = 0
        total_letters_correct = 0
        total_letters_tested  = 0


        if given_lts_rules:
            lts_rules = given_lts_rules
        else:
            lts_rules = lts_learner.GetRules()
        
        if verbose: 
            num_words_incorrect = 0
            print '%6s %6s %6s %24s %48s  |  %s' %('Index', 'Count', 'Right', 'Word', 'Reference', 'Predicted')
 
        for i, (charseq, phoneseq, training_alignments) in enumerate (self.word_alignments_list):
            (predicted_pronun,  
            predicted_alignment) = lts_learner.PredictOneWordPronun (charseq, lts_rules)
            predicted_pronun_str = string.strip (string.join (predicted_pronun))
            correct_pronun       = map ((lambda x: self.name_inversion_table.get(x,x)), phoneseq)
            correct_pronun_str   = string.strip (string.join (correct_pronun))
                
            print '%s\n%s\n%s\n' %(charseq, predicted_pronun_str, correct_pronun_str)
            print predicted_pronun    
            


            for item in training_alignments [:1]:
                one_alignment = item[1]
                char_phoneseq = map ((lambda x: x[1]), one_alignment)
                word = string.join (charseq,'')
                length_diff = len(charseq) - len(phoneseq)
                
                if length_diff not in [-1,0,1]: 
                    #print 'SKIP', word
                    continue
                else:
                    pass #print           

               #print '( word_%04i %s |' %(i+1, word),
               #print '( %s  "' %(word),
                     

                for letter, phoneseq, count in one_alignment:
                    #print letter, phoneseq,
                    for phcode in phoneseq:
                        phone_name = self.name_inversion_table.get (phcode,'?')
                        #print phone_name.upper(),
                    if len (phoneseq) == 0: pass
                        #print '_',
                #print '")',                    

                #pronun = map ((lambda x: self.name_inversion_table.get(x[1],'?')), item[1])
                #print item[1][0], item[1][1], pronun
                    
            
            letters_correct, letters_tested = CompareAlignments (training_alignments, predicted_alignment)
            total_letters_correct += letters_correct
            total_letters_tested  += letters_tested 
      
            correct_prediction = correct_pronun_str == predicted_pronun_str
            if correct_prediction: total_words_correct += 1
                
            if verbose and not correct_prediction: 
                word = string.join (charseq,'')    
                num_words_incorrect += 1    
                print '%6i %6i %6s %24s %48s  |  %s' %(i+1, num_words_incorrect, correct_prediction, word, correct_pronun_str, predicted_pronun_str)
                  
                #T1 = self.name_inversion_table    
                #T2 = lts_learner.GetPhoneNameInvTable()
                #print map ((lambda x: T1.get(x,'?')), phoneseq)
                #print map ((lambda x: T2.get(x,'-')), predicted_pronun)
                #sys.exit()
                """    
                print predicted_alignment
                for item in predicted_alignment:
                    if item[2]:
                        pred_prod = item[2][0]
                        pred_rule = pred_prod[2]    
                        print '  ', pred_prod
                """        
        if verbose: print
            
        return (total_words_correct, len(self.word_alignments_list)), \
               (total_letters_correct, total_letters_tested)
    pass
                
# end class.
# ----------



# --------------------------------------------------------------------------------------------------
def TestRuleSystem (lts_learner, lts_rules, verbose=False):
    
    all_results = []
        
    for alignment_pathname in prog_args:
        if os.path.exists (alignment_pathname):
            t1 = time.time()
            lts_measurer = Measurer()    
            lts_measurer.InitWithAlignments (alignment_pathname)
            if verbose: print 'Reading alignments from %s in %3.2f s' %(alignment_pathname, time.time()-t1)
                
            all_results.append (lts_measurer.MeasurePredictionAccuracy (lts_learner, lts_rules, verbose=True))
                
    if len (all_results) > 0:
        total_words_correct  = sum (column (column (all_results)))
        total_words_tested   = sum (column (column (all_results), 1))
        total_chars_correct  = sum (column (column (all_results,1)))
        total_chars_tested   = sum (column (column (all_results,1), 1))
        word_percent_correct = 100.0 * total_words_correct / max (1, total_words_tested)
        char_percent_correct = 100.0 * total_chars_correct / max (1, total_chars_tested)
            
        if verbose:
            print ' Threshold %i' %(threshold_value)
            print ' Total words correct: %6.3f  %8i %8i' %(word_percent_correct, total_words_correct, total_words_tested)
            print ' Total chars correct: %6.3f  %8i %8i' %(char_percent_correct, total_chars_correct, total_chars_tested)
            print '--------------------\n'

    return (total_words_correct, total_words_tested), (total_chars_correct, total_chars_tested)
pass
    



# --------------------------------------------------------------------------------------------------
# Measure rules sets reduced by different thresholds.                                               
    
def ComputeAccuracyVsRulesCurve (lts_learner, max_threshold = 9999999999):

    rule_counts_list = list (set (column (lts_learner.GetRulesByCount())))
    rule_counts_list.sort()

    
    print '%6s %8s %8s' %('Thresh', 'Rules', 'Chars')
    for thr in rule_counts_list:
        lts_rules, num_lts_rules, num_lts_chars = lts_learner.ThresholdRules (thr)
        filename = 'rules/lexrules_%s.scm' %(string.zfill(num_lts_rules,5))
        print '%6i %8i %8i' %(thr, num_lts_rules, num_lts_chars)
        lts_learner.WriteOutFestivalRules (filename, 'cmu_us', lts_rules)
    sys.exit()
        
        
        #new_lts_rules, num_lts_rules, num_lts_chars = lts_learner.ThresholdRules (3)
        #lts_learner.WriteOutFestivalRules ('afile', new_lts_rules)
     
 
    print '%4s %6s %6s %8s %8s' %('Num', 'Thresh', 'Rules', 'Words', 'Chars')
        
    for i, threshold in enumerate (rule_counts_list):
        if threshold > max_threshold: continue
        lts_rules, num_lts_rules, num_lts_chars = lts_learner.ThresholdRules (threshold)
            
        word_perf, char_perf = TestRuleSystem (lts_learner, lts_rules)
        word_percent_correct = 100.0 * word_perf[0] / word_perf[1]
        char_percent_correct = 100.0 * char_perf[0] / char_perf[1]
            
        print '%4i %6i %6i %8.3f %8.3f  '  \
            %(i+1, threshold, num_lts_rules, word_percent_correct, char_percent_correct), \
              word_perf, char_perf
    print
pass



# --------------------------------------------------------------------------------------------------
def TestRuleLearnerWeb (num_words_to_use = 10):
    
    lts_learner.ProvidePronunciationOracle (dict_oracle)
 
    for i in range (num_words_to_use):
        outfile = file ('a.html', 'w')
        w1 = lts_learner.GetNextWord() 
        p1 = dict_oracle.GetWordPronunciation (w1)
        lts_learner.PrepareWebPageWithNewWord (outfile, w1)
        lts_learner.SubmitPronunciation (w1, p1)
        outfile.close()    
         


    
# --------------------------------------------------------------------------------------------------
def TestRuleLearnerSrvr (use_word_selector=False, num_words_to_use = 10):
    
    # ------------------------------------------------------------------------------------
    def PrintOut (word, pronun):
        
        char_val_lst = map ((lambda ch: ord(ch)), word)
            
        if len(char_val_lst) > 0:
            max_char_val = max (char_val_lst)
        else:
            max_char_val = 0        
        
        if max_char_val > 255:
            print 'TestRuleLearnerSrvr: %24s <- %s' %(pronun, char_val_lst)
        else:        
            print 'TestRuleLearnerSrvr: %24s -> %s' %(word, pronun)
                  


    N = min (num_words_to_use, len(word_pronun_list))

    if use_word_selector:
        print
        for i in range(N):
            #print i, xmlrpclib.dumps ((1,'z', 'abc\xf3'), 'GetNextWord', encoding = 'utf-8')
            w1 = lts_learner.GetNextWord()
            p1 = string.join (dict_oracle.GetWordPronunciation (w1))
            PrintOut (w1, p1)
            lts_learner.SubmitPronunciation (w1, p1)
        print
    
    else:    
        print
        for i in range(N):
            charseq, phoneseq, ignore = word_pronun_list[i]
            w1 = string.join (charseq,'')
            p1 = string.join (phoneseq, ' ')
            PrintOut (w1, p1)
            lts_learner.SubmitPronunciation (w1, p1)            # for LTS_RuleLearnerSrvr
           #lts_learner.SubmitPronunciation (charseq, phoneseq) # for LTS_RuleLearner
        print
    
    lts_learner.WriteAllowablesFile ('a_allowables.scm')
    LTS_IO.WriteOutRules ('a.lts_rules', lts_learner.GetRules())
pass



# ---------------------------------------------------------------------------------------------
def PrintBasicInfo (word_pronun_list):
    

    # -----------------------------------------------------------------------------------------
    def PrintList (item_count_tbl, message, conversion_table={}):
        
        print message
        
        total_cnt = 0    
        item_list = item_count_tbl.keys()
        item_list.sort()  
              
            
        for i, item in enumerate (item_list):
            count = item_count_tbl[item]
            total_cnt += count    
            print '%3i %6i  %s' %(i+1, item_count_tbl[item], conversion_table.get(item,item))
        print '%10i\n' %(total_cnt)
    pass
    

    # create a pronunciation oracle and write some info
        
    if not word_pronun_list:
        print 'Empty word list\n'
        return        

    dict_oracle   = PronunciationOracle.T (word_pronun_list, disguise_phone_names = False)
    word_selector = WordSelector.T (word_pronun_list)                                        

    letter_counts, phone_counts = dict_oracle.GetLettersAndPhoneCounts() 
    ngram_size_list = map ((lambda x: len(x)), word_selector.GetLetterStats())    
            
       
    print 'Number of words in lexicon: %i' %(len (word_pronun_list))
    print 'Num unique letters, phones: %i %i' %(len(letter_counts), len(phone_counts)) 
    print 'Number n-grams, many sizes: %s\n' %(ngram_size_list)  
        
    PrintList (letter_counts, 'Letter List')
    PrintList (phone_counts,  'Phone List', {}) #phone_name_conversions)
pass
     




# -----------------------------------------------------------------------------------------
def CompareBySize (item1, item2):
    
    word1 = item1[0]
    word2 = item2[0]

    if   len(word1) < len(word2): return -1
    elif len(word1) > len(word2): return +1
    else: return word1 < word2
pass
    


# -----------------------------------------------------------------------------------------
def SortWordsByCoverage (given_word_list, verbosity=False):
    
    new_word_pronun_list = []
        
    total_letters = 0
    N = len (given_word_list)    
        
    try:
        for i in range (N):
            ans = word_selector.SelectOneWord_Ver3 (verbose=verbosity)
            w1  = tuple (ans[0])
            p1  = tuple (dict_oracle.GetWordPronunciation (w1))
            word_selector.HappyWithWord(w1)
            new_word_pronun_list.append ((w1, p1))
            total_letters += len(w1)
                
            if verbosity: 
                score = ans[2]
                word  = string.join (w1,'')
                print '%3i %4i. %6i  %s' %(len(w1), i+1, total_letters, word)
                    
    except IndexError:
        pass            
    
    return new_word_pronun_list
pass
    

# -----------------------------------------------------------------------------------------
def SortWordsByCoverage2 (given_word_list, verbosity=False):
    
    new_word_pronun_list = []
        
    total_letters = 0
    N = len (given_word_list)    
        
    ngrams_in_lts = []

    try:
        for i in range (N):
            ans = word_selector.SelectOneWord_Ver4 (ngrams_in_lts, verbose=verbosity)
                
            w1  = tuple (ans[0])
            p1  = tuple (dict_oracle.GetWordPronunciation (w1))
            word_selector.HappyWithWord(w1)
            new_word_pronun_list.append ((w1, p1))
            total_letters += len(w1)
                
            if verbosity: 
                score = ans[2]
                word  = string.join (w1,'')
                print '%3i %4i. %6i  %s' %(len(w1), i+1, total_letters, word)
               

            #ngrams = WordSelector.NgramsInWord (w1)
            #print ngrams[1].keys()
            #ngrams_in_lts.extend (ngrams[1].keys())        


            lts_learner = LTS.T() 
            num_words   = int (option_tbl['--numwords'])
            max_window  = int (option_tbl['--window'])   
            alignment_file_pathname = option_tbl.get('--align','')

            LoadAlignments (lts_learner, alignment_file_pathname)
                
            TestRuleLearnerBatch (lts_learner,
                                  new_word_pronun_list,
                                  num_words_to_use = len(new_word_pronun_list),
                                  max_context_window_width = max_window)
 
            
            lts_rules = lts_learner.GetRules()
                
            for lhs in lts_rules.keys():
                rule_chain = lts_rules[lhs]
                for context, rhs, score in rule_chain:
                    ngram = tuple (string.join (context,''))
                    ngrams_in_lts.append (ngram)
            
               
            if i > 99: return new_word_pronun_list
                                        
    except IndexError, msg:
        print '\nError', msg
    
    return new_word_pronun_list
pass
  




# --------------------------------------------------------------------------------------------------
def LoadAlignments (lts_learner, word_alignment_pathname, verbose=False):
    
    t1 = time.time()
        
    if os.path.exists (word_alignment_pathname) and os.path.isfile (word_alignment_pathname):
        if verbose: print 'Loading allowables %s in' %(word_alignment_pathname),
        lts_learner.LoadStateInfoAlignment (word_alignment_pathname)
        if verbose: print '%3.2f seconds\n' %(time.time()-t1)
    else:
        print 'Error: alignment files does not exist', word_alignment_pathname
    
    if verbose > 1:        
        lts_learner.WriteProductionsSummary (sys.stdout)
 
pass            



# --------------------------------------------------------------------------------------------------
# Note: this modifies word_pronun_list                                                              
    
def LearnAllowables (lts_learner, word_pronun_list, num_words_to_use, progress_file = sys.stdout):
             
    t1 = time.time()
    N  = min (len(word_pronun_list), num_words_to_use)

    dict_oracle = PronunciationOracle.T (word_pronun_list, disguise_phone_names = True)
    phone_table = dict_oracle.GetPhoneNameInversionTable()    
    word_pronun_list = dict_oracle.GetFullPronunciationList()
        
    lts_learner.SetPhoneNameInvTable (phone_table)
        
    lts_learner.BatchwiseDiscoverAllowables (word_pronun_list[:N], 
                                             write_progress_files = 0, 
                                             progress_output_file = progress_file, 
                                             verbose = False)
        
    print 'Discovered allowables in %3.2f seconds\n' %(time.time()-t1)
        
    #lts_learner.WriteProductionsSummary (sys.stdout)
pass


     
# --------------------------------------------------------------------------------------------------
def Learn_LTS_Rules (lts_learner, 
                     word_pronun_list, 
                     num_words_to_use, 
                     max_context_window_width = 1): 
    
    t1 = time.time()
    N  = min (len(word_pronun_list), num_words_to_use)
       
    #print 'IS', num_words_to_use, lts_learner.GetNumTrainingWords(), len(word_pronun_list)
    """    
    if num_words_to_use < lts_learner.GetNumTrainingWords():
        explicit_wordset = set (column (word_pronun_list[:N]))
        lts_rule_systems = lts_learner.BatchwiseDiscoverRules (max_context_window_width, explicit_wordset)
    else:
    """    
        
    lts_rule_systems = \
        lts_learner.BatchwiseDiscoverRules (max_context_window_width, 
                                            run_with_low_memory_usage = option_tbl.has_key ('--low_memory'),
                                            verbose=True)
            
    print 'Discovered LTS rules in %3.2f seconds\n' %(time.time()-t1)
     
    return lts_learner
pass        


        
# --------------------------------------------------------------------------------------------------
def TestRuleLearner (lts_learner, lts_measurer, verbose=False):
    
   
    #total_training_words   = min (len(word_pronun_list), num_words_to_use)
    #total_training_letters = sum (map ((lambda x: len(x[0])), word_pronun_list[:total_training_words]))

    if verbose: lts_learner.WriteOutRules (sys.stdout)    
        
    one_rule_system      = lts_learner.GetRules()
    number_of_lts_rules  = sum (map ((lambda x: len(x)), one_rule_system.values()))
    word_perf, char_perf = lts_measurer.MeasurePredictionAccuracy (lts_learner, one_rule_system, verbose=False)
        
    word_percent_correct = 100.0 * word_perf[0] / max (1, word_perf[1])
    char_percent_correct = 100.0 * char_perf[0] / max (1, char_perf[1])
    
    print '    Number LTS rules:  %i' %(number_of_lts_rules)
   #print '  Num training words: %i' %(total_training_words)
   #print '  Num training chars: %i' %(total_training_letters)
   #print 'Number words correct: %6.2f  %6i %6i %6i %6i' %(word_percent_correct, word_perf[0], word_perf[1], total_training_words, total_training_letters)
    print 'Number words correct: %6.2f  %6i %6i' %(word_percent_correct, word_perf[0], word_perf[1])
    print 'Number chars correct: %6.2f  %6i %6i' %(char_percent_correct, char_perf[0], char_perf[1])
    print '--------------------\n'
    print
        
    return word_perf, char_perf
pass
    


# ------------------------------------------------------------------------------
# Why isn't this working?                                                       
def linetrace (frame, event, arg):
    if event == "line":
        lineno = frame.f_lineno
        print "line", lineno

sys.settrace (linetrace)

 

# ------------------------------------------------------------------------------------------
# Comment:  Copied this from LTS_RuleLearner. Spreading the code around is not the best of  
#           ideas, but was done in the name of expedience.                                  
     
def WriteOneLexEntry (outfile, word, undisguised_phoneseq, lex_format='janus'):
    
    pronun = string.join (undisguised_phoneseq)
     
    if lex_format.lower() == 'janus':
        outfile.write ('%-24s ' %(word))
            
        if len(undisguised_phoneseq) == 0:
            outfile.write ('{}\n')
        else:
            outfile.write ('{{%s WB}' %(undisguised_phoneseq[0]))
                
            for ph in undisguised_phoneseq[1:-1]:
                outfile.write (' %s' %(ph))
                    
            if len(undisguised_phoneseq) >= 2:
                outfile.write (' {%s WB}' %(undisguised_phoneseq[-1]))
            outfile.write('}\n')
                
    elif lex_format.lower() == 'sphinx':
        outfile.write ('%s %s\n' %(word, pronun))
            
    elif lex_format.lower() == 'festival':
        outfile.write ('("%s" nil (%s))\n' %(word, pronun))
                        
pass                        


# ----------------------------------------------------------------------------------------------
# Some usages:                                                                                  
# 1.  prog --info                                                                               
# 2.  prog --dict  dict_filename                                                                
# 3.  prog --dict  dict_filename --info                                                         
# 4.  prog --align alignment_filename                                                           
# 5.  prog --align alignment_filename --info                                                    
# 6.  prog --rules lts_rules_filename                                                           
# 7.  prog --rules lts_rules_filename --info                                                    
# 8.  prog --batch --dict  dict_filename                                                        
# 9.  prog --batch --dict  dict_filename --align alignment_filename                             
# 10. prog --batch --dict  dict_filename --align alignment_filename --rules lts_rules_filename  
# 11. prog --batch --align alignment_filename                                                   
# 12. prog --batch --align alignment_filename --rules lts_rules_filename                        
    
# 13. prog --batch --align alignment_filename --learn_from_align                                
# 14. prog --batch --align alignment_filename --learn_from_align --rules lts_rules_filename     
# 15. prog --batch --align alignment_filename --rules lts_rules_filename                        
# 16. prog --batch --rules lts_rules_filename                                                   

if __name__ == '__main__':
        
    flag_list = [ \
        'lexlist=',
        'dict=',                # a pronunciation dictionary in festival format     
        'align=',               # a pickled alignment file created by LTS_Allowables
        'test',                 # a pickled alignment file used for testing rules   
        'rules=',               # a pickled lts rule file created by LTS_RuleSystem 
        'numwords=',            # number of entries from word list to use           
        'window=',              # maximum width of letter context window to use     
        'info=',                # print basic info about dictionary and lts rules   
        'batch',                # read in or learn lts rules in batch mode          
        'measure_curve',        # measure accuracy at various rule threshold values 
        'low_memory',           # learn 1 letter at at time to keep memory usage low
        'predict_outfile=',     # name of outfile file containing predictions       
        'predict_format=',      # format of predictions: janus, sphinx, festival    
        'batchramp',                                           # type of test to run
        'alpha', 'reverse', 'bysize', 'random', 'coverage',    # word ordering flags
        'web',    
        'xmlrpc', 
        'port=',
        'numreps']
        
    opt_list, prog_args = getopt.getopt (sys.argv[1:], '', flag_list)
    option_tbl = dict (opt_list)



    # Initialize a 'blank' rule system and measurer.
        
    lts_learner  = LTS.T()
    word_pronun_list = []
    phone_inversion_table = {}        # keep this here?

    

    # --dict option                               
    #   read in a festival pronuncation dictionary
        
    if option_tbl.has_key ('--reverse'): 
        reverse_dict_entries = True
    else:        
        reverse_dict_entries = False
        
        
    if option_tbl.has_key ('--dict'): 
        dictionary_pathname = option_tbl ['--dict']
            
        if os.path.exists (dictionary_pathname):
            word_pronun_list = DictionaryIO.ReadFestivalDictionary (dictionary_pathname, 
                                                                    words_only=False, 
                                                                    reverse_direction=reverse_dict_entries)
                
            print 'Reading dictionary %s  %i\n' %(dictionary_pathname, len(word_pronun_list))
                    
    elif option_tbl.has_key ('--lexlist'):
        dictionary_pathname = option_tbl ['--lexlist']

        if os.path.exists (dictionary_pathname):
            word_pronun_list = DictionaryIO.ReadLexiconFileWithCounts (dictionary_pathname, words_only=False)
            print 'Reading dictionary %s  %i\n' %(dictionary_pathname, len(word_pronun_list))
            
            if not word_pronun_list: 
                print 'Error: zero length pronunciation list!\n'
                sys.exit()
                
              
    # --rules option                        
    #   read in lts rules from a pickle file
        
    if option_tbl.has_key ('--rules'):
        rule_file_pathname = option_tbl.get('--rules')
            
        if os.path.exists (rule_file_pathname):    
            t1 = time.time()
            lts_learner.LoadStateInfoRules (rule_file_pathname)
            print 'Reading LTS rules from %s in %3.2f s\n' %(rule_file_pathname, time.time()-t1)    
        else:
            print 'Cannot find %s' %(rule_file_pathname)        
            

    #if option_tbl.has_key('--align'):
    #    alignment_file_pathname = option_tbl.get('--align','')
    #    LoadAlignments  (lts_learner, alignment_file_pathname, verbose=3)
    #sys.exit()

    # --info option                                              
    #   print basic information about the word list, if requested
    #   and print basic information about LTS rules, if it exists
    
    if option_tbl.has_key ('--info'):    
        PrintBasicInfo (word_pronun_list)
           
        phone_names_list = lts_learner.GetPhoneNameInvTable().items()
        phone_names_list.sort()
            
        print 'Disguised Phone Names'        
        for hidden_name, real_name in phone_names_list:
             print '%4s -> %s' %(hidden_name, real_name)
        print        
            
        info_basename = option_tbl['--info']
            
        # if --info is followed by another --flag, this prevents writing out
        # to the files --flag.lst and --flag.prod.                          
            
        if len (info_basename) >= 2 and info_basename[:2] == '--':
            info_basename = 'stdout'
                
        if info_basename in ['stdout','-']:
            lts_learner.WriteProductionsSummary (sys.stdout)
            lts_learner.WriteOutRules (sys.stdout)
        else:
            filename_prods = info_basename + '.prod'
            filename_rules = info_basename + '.lts'
            lts_learner.WriteProductionsSummary (filename_prods)
            lts_learner.WriteOutRules (filename_rules)

        histo = lts_learner.GetRuleHistogram()
        width_list = histo.keys()
        width_list.sort()
            
        print '%5s %s' %('Width', 'Rules')
        for context_width in width_list:
            num_rules = histo [context_width]
            print '%5i %i' %(context_width, num_rules)                
        print 'Total %i' %(sum(histo.values()))
            

         

    # modify the word pronunciation list
    num_repetitions = int (option_tbl.get ('--numreps',1))
        
    if option_tbl.has_key ('--alpha'):
        word_pronun_list.sort()
            
    #if option_tbl.has_key ('--reverse'):
    #    word_pronun_list.reverse()
            
    elif option_tbl.has_key ('--bysize'):
        word_pronun_list.sort (cmp = CompareBySize)
            
    elif option_tbl.has_key ('--random'):
        random.seed()
            
    elif option_tbl.has_key ('--coverage'):
        word_pronun_list = SortWordsByCoverage2 (word_pronun_list, verbosity=True)
        DictionaryIO.WriteFestivalDictionary ('newlex.scm', word_pronun_list, phone_inversion_table)
        sys.exit()


               
    # --batch option
    elif option_tbl.has_key ('--batch'):
        num_words   = int (option_tbl.get('--numwords', len(word_pronun_list)))
        max_window  = int (option_tbl.get('--window',7))
            
        alignment_file_pathname = option_tbl.get('--align','')
                   
        # Case 1. Learn allowables and build alignments from dictionary 
        #         then learn the lts rules from the learned alignments. 
        # Case 2. Load alignments from pickle file then learn lts rules.
            
        if option_tbl.has_key ('--dict'):
            LearnAllowables (lts_learner, word_pronun_list, num_words)

            Learn_LTS_Rules (lts_learner, word_pronun_list, num_words,
                             max_context_window_width = max_window)
            
        elif option_tbl.has_key('--align'):
            LoadAlignments  (lts_learner, alignment_file_pathname, verbose=1)

            Learn_LTS_Rules (lts_learner, word_pronun_list, num_words,
                             max_context_window_width = max_window)
                                     
        
        # If it doesn't already exist, pickle the alignment data.
        # else, measure the accuracy of the lts rule system      
            
        if alignment_file_pathname: #and not os.path.exists (alignment_file_pathname):
            print 'Pickling alignment info to %s\n' %(alignment_file_pathname)
            lts_learner.PickleStateInfoAlignment (alignment_file_pathname)

        # If it doesn't already exist, pickle lts rules rules.
            
        if option_tbl.has_key ('--rules'):
            lts_rule_file_pathname = option_tbl['--rules']
                
            if lts_rule_file_pathname.find('pkl') > 0:
                productions_pathname   = lts_rule_file_pathname.replace ('pkl','prod')
                lts_rule_text_pathname = lts_rule_file_pathname.replace ('pkl','txt')
            else:        
                productions_pathname   = lts_rule_file_pathname + '.prod'
                lts_rule_text_pathname = lts_rule_file_pathname + '.txt'

            #if not os.path.exists (lts_rule_file_pathname):
            print 'Pickling lts rule info to %s\n' %(lts_rule_file_pathname)
            lts_learner.PickleStateInfoRules (lts_rule_file_pathname)
                
            lts_learner.WriteOutRules (lts_rule_text_pathname)    
            lts_learner.WriteProductionsSummary (productions_pathname)
            
        # this still needs to be improved
        #pl = WordSelector.SortWordListByNgramCoverage (lts_learner, word_pronun_list, phone_inversion_table)
        #DictionaryIO.WriteFestivalDictionary ('newlex.scm', pl, phone_inversion_table)
 

    
    # --predict option                                                  
                
    elif option_tbl.has_key ('--predict_outfile') and option_tbl.has_key ('--rules'):
        
        print 'PREDICTING %i words' %(len(word_pronun_list))
            
        import codecs
        outfile = codecs.open (option_tbl['--predict_outfile'], 'w', 'utf-8')
        format = option_tbl.get ('--predict_format', 'janus')
            
        for cnt, item in enumerate (word_pronun_list):
            word = string.join (item[0],'')
            pred = lts_learner.PredictOneWordPronun (word)
            pron = string.replace (string.join (pred[0]), '_', '')
            pron = string.join (pron.split())
            #outfile.write ('%4i %40s  %s\n' %(cnt+1, pron, word))
            WriteOneLexEntry (outfile, word, string.split(pron), format)
        outfile.close()
            
    

    # --test option                                                     
    #   Read in a list of pickle files containing alignment information 
    #   and test each one. If there is more than one test file compute  
    #   the overall performance too.                                    
                
    elif option_tbl.has_key ('--test'):
        all_results = []

            
        alignment_file_pathname = option_tbl.get('--align','')
 
        #for alignment_pathname in prog_args:
        for alignment_pathname in [alignment_file_pathname]:
            if os.path.exists (alignment_pathname):
                t1 = time.time()
                lts_measurer = Measurer()
                lts_measurer.InitWithAlignments (alignment_pathname)
                print 'Reading alignments from %s in %3.2f s\n' %(alignment_pathname, time.time()-t1)
                #all_results.append (TestRuleLearner (lts_learner, lts_measurer))
                    
        lts_measurer.WriteWagonTrainingData('wagon.data')
            
                     
        if len (all_results) > 1:
            total_words_correct  = sum (column (column (all_results)))
            total_words_tested   = sum (column (column (all_results), 1))
            total_chars_correct  = sum (column (column (all_results,1)))
            total_chars_tested   = sum (column (column (all_results,1), 1))
            word_percent_correct = 100.0 * total_words_correct / max (1, total_words_tested)
            char_percent_correct = 100.0 * total_chars_correct / max (1, total_chars_tested)
                 
            print ' Total words correct: %6.3f  %8i %8i' %(word_percent_correct, total_words_correct, total_words_tested)
            print ' Total chars correct: %6.3f  %8i %8i' %(char_percent_correct, total_chars_correct, total_chars_tested)
            print '--------------------\n'



    # --measure_curve
    elif option_tbl.has_key ('--measure_curve') and option_tbl.has_key ('--rules'):
        ComputeAccuracyVsRulesCurve (lts_learner)
            
            
            
    # --batchramp
    elif option_tbl.has_key ('--batchramp'):
        import LTS_RuleSystem as LTS_Learner

        alignment_file_pathname = option_tbl.get('--align','')
            

        if option_tbl.has_key ('--align'):
            max_words  = int (option_tbl['--numwords'])
            max_window = int (option_tbl['--window'])   

            for i in range (num_repetitions):
                if option_tbl.has_key ('--random'):
                    random.shuffle (word_pronun_list)

                #for num_words in range (50, min(501,max_words+1), 50):
                    
                for num_words in range (1, max_words+1, 1):
                    print '%i words of %i' %(num_words, max_words)
                        
                    lts_learner = LTS_Learner.T()

                    if option_tbl.has_key('--align'):
                        LoadAlignments (lts_learner, alignment_file_pathname)
                            
                        TestRuleLearnerBatch (lts_learner, 
                                              word_pronun_list,
                                              num_words_to_use = num_words,
                                              max_context_window_width = max_window)
                                                
                    elif option_tbl.has_key ('--dict'):
                        LearnAllowables (lts_learner, word_pronun_list, num_words)

                        TestRuleLearnerBatch (lts_learner,
                                              word_pronun_list,
                                              num_words_to_use = num_words,
                                              max_context_window_width = max_window)
            

            """
            for num_words in range (500, max_words+1, 500):
                print '%i words of %i' %(num_words, max_words)
                    
                lts_learner = LTS_Learner.T()
                    
                if option_tbl.has_key('--learn_from_align'):
                    TestRuleLearnerBatch (word_pronun_list,
                                            num_words_to_use         = num_words,
                                            word_alignment_pathname  = alignment_file_pathname,
                                            max_context_window_width = max_window))
                elif option_tbl.has_key ('--dict'):
                    TestRuleLearnerBatch (word_pronun_list,
                                            num_words_to_use = num_words,
                                            max_context_window_width = max_window)
            """
            

             
    # --xmlrpc
    elif '--xmlrpc' in option_tbl:
        import LTS_RuleLearnerSrvr

        if '--port' in option_tbl:
            import xmlrpclib
            import socket    
                
            port_number = option_tbl['--port']
                
            try:
                lts_learner = xmlrpclib.Server ('http://localhost:%s' %(port_number), encoding = 'utf-8')
            except socket.error, msg:
                print 'Error: %s to port %s' %(msg, port_number)
                sys.exit()    

        else:
            lts_learner = LTS_RuleLearnerSrvr.T (word_pronun_list)
                    

        dict_oracle = PronunciationOracle.T (word_pronun_list, disguise_phone_names = True)
        TestRuleLearnerSrvr (use_word_selector=False, num_words_to_use=100)
                
            
    # --web
    elif option_tbl.has_key ('--web'):
        import LTS_RuleInterfaceWeb
            
        lts_learner = LTS_WebInterface.T (word_list) 
        TestWebLearner()

print 'test_lts_learner: very end'

