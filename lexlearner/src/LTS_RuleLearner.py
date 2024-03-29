# LTS_RuleLearner.py                                                                                            
#===================                                                                                            
# 0.02.004  19-Sep-2007  jmk  Class multiple-inherits instead of having an embedded WordSelector object.        
# 0.02.003  07-May-2007  jmk  SubmitPronunciation switches to incremental learning when batch learning slows.   
# 0.02.002  12-Apr-2007  jmk  Use SimpleWordSelector.                                                           
# 0.02.001  14-Mar-2007  jmk  Revised to support utf-8.                                                         
# 0.01.001  26-Oct-2005  jmk  Created.                                                                          
# ---------------------                                                                                         

import codecs 
import os, sys
import string
import StringIO
import time
    
import LTS_IO
import LTS_RuleSystem
import LTS_RuleSystemTrain
import SimpleWordSelector
import TwostageWordSelector    
import ConfigPath
import Logger



# -------------------------------------------------------------------------------------------------
# before: class T (LTS_RuleSystemTrain.T, SimpleWordSelector.T):
    
class T (LTS_RuleSystemTrain.T, TwostageWordSelector.T):
     

    # ---------------------------------------------------------------------------------------------
    def __init__ (self, prompt_word_list, corpus_word_list, unknown_phone_symbol='_?_'):
        
        self.textlog = Logger.T (Logger.Summary_Level)
        self.textlog.OpenOutputFile('lexlearner.log')
        self.textlog.write (Logger.GetFunctionName(__name__))
        
        # should really process this to handle strings and lists
        # and to automatically detect/insert endpoint hashes    
            
        LTS_RuleSystemTrain.T.__init__(self, unknown_phone_symbol)
       #SimpleWordSelector.T.__init__(self, corpus_word_list)
        TwostageWordSelector.T.__init__(self, prompt_word_list, corpus_word_list)
             
        self.full_word_list = corpus_word_list
             
        self.production_counts = []
        self.word_pronun_list  = []
        self.word_pronun_table = {}
        self.word_pronun_exper = {}
        self.non_words_set = set()
        self.last_lts_learning_time = 0.0
    pass


    # ----------------------------------------------------------------------------------------------
    # Old: these return values don't apply to the SimpleWordSelector                                
    # word_charseq, triggering_ngram, ngram_score = self.word_selector.SelectOneWord(False)         
        
    # ---------------------------------------------------------------------------------------------
    def GetSubmittedPronunciation (self, char_seq):
        self.textlog.write (Logger.GetFunctionName(__name__))
        return self.word_pronun_table.get (char_seq, [])


    # ---------------------------------------------------------------------------------------------
    def GetExperimentalPronunciation (self, char_seq):
        self.textlog.write (Logger.GetFunctionName(__name__))
        return self.word_pronun_exper.get (char_seq, [])

        
    # ---------------------------------------------------------------------------------------------
    def GetRecentWordPronuns (self):
        self.textlog.write (Logger.GetFunctionName(__name__))
        return self.word_pronun_list

        
    # ---------------------------------------------------------------------------------------------
    # Eliminate this method?                                                                       
        
    def GetAllowablesReport (self):
        self.textlog.write (Logger.GetFunctionName(__name__))
        
        # ---------------------------------
        def FilterReport (given_string):
            
            line_list = string.split (given_string, '\n')
                
            for cnt, line in enumerate (line_list):
                if string.find (line, 'LTS') > -1: 
                    return line_list[cnt+1:-1]
            return [] 
        pass

        try:
            string_file = StringIO.StringIO()
            LTS_IO.WriteProductionsSummary (string_file, self.total_production_counts)
            report = FilterReport (string_file.getvalue())
        except AttributeError:
            report = ''
                    
        return report 
    pass
                    


    # ---------------------------------------------------------------------------------------------
    def GetRules (self):
        self.textlog.write (Logger.GetFunctionName(__name__))
        return self.lts_rule_system


    # ---------------------------------------------------------------------------------------------
    def RemoveFromLexicon (self, charseq):
        self.textlog.write (Logger.GetFunctionName(__name__))
        self.UnhappyWithWord (''.join(charseq))
        if charseq: self.non_words_set.add (charseq)
        return len (self.non_words_set)


    # ---------------------------------------------------------------------------------------------
    def SubmitExperimentalPronunciation (self, charseq, pronunciation):
        self.textlog.write (Logger.GetFunctionName(__name__))
        self.word_pronun_exper [charseq] = pronunciation
        return True    


    # ---------------------------------------------------------------------------------------------
    def SubmitPronunciation (self, charseq, pronunciation, stype='batch'):
        self.textlog.write (Logger.GetFunctionName(__name__))

        self.HappyWithWord (''.join(charseq))
        self.word_pronun_list.append ((charseq, pronunciation, 1))
        self.word_pronun_table [charseq] = pronunciation

        t1 = time.time()

        #if self.last_lts_learning_time < 1.0:
        if stype == 'batch':
            self.production_counts = self.BatchwiseDiscoverAllowables (self.word_pronun_list)
            self.BatchwiseDiscoverRules()
            t2 = time.time()    
            self.last_lts_learning_time = t2-t1
            #print 'Learn time (batch): %3.3f' %(self.last_lts_learning_time)
        else:
            found_solutions = self.FindAlignmentSequences (charseq, pronunciation, verbose=False)
            self.UpdateProductionsInSolution (charseq, pronunciation, found_solutions)
            t2 = time.time()    
            #print 'Learn time (incre): %3.3f' %(t2-t1)
                      
        return True
    pass
        


    # ---------------------------------------------------------------------------------------------
    def DisguisePhonemeNames (self, given_phoneset):
        self.textlog.write (Logger.GetFunctionName(__name__))
     
        disguised_phoneme_names_fwd = {}
        disguised_phoneme_names_inv = {}

        phoneme_list = list(given_phoneset)
            
        for cnt, phoneme in enumerate (sorted (phoneme_list)):
            phoneme_number = '%02i' %(cnt+1)    
            disguised_phoneme_names_fwd [phoneme] = phoneme_number
            disguised_phoneme_names_inv [phoneme_number] = phoneme
            
        self.SetPhoneNameInvTable (disguised_phoneme_names_inv)
        self.phoneme_set = given_phoneset    
    pass
        

               
    # ---------------------------------------------------------------------------------------------
    def PrimeWithPronunciations (self, given_pronun_list, include_punctuation=True):
        self.textlog.write (Logger.GetFunctionName(__name__))
        
        # Assuming all punctuation is silent is a cheap trick, 
        # but helpful in a non-general, non-international way. 
            
        if include_punctuation:    
            for letter in string.punctuation:
                self.word_pronun_list.append ((letter,(),1))
            
        # Add the given pronunciations
            
        words_with_pronun = 0

        for word, phoneme_seq, count in given_pronun_list:
            if phoneme_seq:
                disguised_seq = map ((lambda x: self.phone_name_disguise_table.get(x,x)), phoneme_seq)
                self.word_pronun_list.append ((word, disguised_seq, count))
                self.word_pronun_table[word] = disguised_seq   
                words_with_pronun += 1

        # learn these simple G2P relations
            
        t1 = time.time()
        self.BatchwiseDiscoverAllowables (self.word_pronun_list, verbose=False)
        self.BatchwiseDiscoverRules (verbose=False) 
        t2 = time.time()    
 
        # set the learning time
        self.last_lts_learning_time = t2-t1
            
        return words_with_pronun
    pass
                


    # ----------------------------------------------------------------------------------------------
    def WriteOutLexicon (self, lex_format = 'Janus',
                               filename1  = 'dictionary.lex',
                               filename2  = 'unknown_words.lex',
                               filename3  = 'non_words.lex',
                               verbose    = True):
                                
        self.textlog.write (Logger.GetFunctionName(__name__))
        

        # ------------------------------------------------------------------------------------------
        def WriteOneEntry (outfile, word, phoneseq):
            
            undisguised_phoneseq = map ((lambda x: self.phone_name_inverse_table.get(x,x)), phoneseq)
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
            


        # ------------------------------------------------------------------------------------------
        def CheckPathnameDirectories():    
            
            for filename in [filename1, filename2, filename3]:
                directory, name = os.path.split (filename)
                if directory and not os.path.exists(directory):
                    os.makedirs (directory)
                if verbose:
                    print 'Writing', filename

            

        CheckPathnameDirectories()

        num_known_words = 0
            
        outfile1 = codecs.open (filename1, 'w', 'utf-8')
        if lex_format.lower() != 'festival':
            outfile2 = codecs.open (filename2, 'w', 'utf-8')
            outfile3 = codecs.open (filename3, 'w', 'utf-8')
        
            
        # write out known pronunciations
        word_list = sorted (self.word_pronun_list) 
            
        for charseq, phoneseq, count in word_list:
            if charseq and phoneseq:
                word = string.join (charseq,'')
                WriteOneEntry (outfile1, word, phoneseq)

        # write out remaining pronuncations (but not for festival dictionary)   
        # the word can go to one of three places:                               
        #   1. the main pronunciation dictionary                                
        #   2. the unknown_words lexicon (words lexlearner can't pronounce)     
        #   3. the non_words lexicon (words that the user dicarded)             
                
        if lex_format.lower() != 'festival':
            word_list = sorted (self.full_word_list)    
                
            for cnt, item in enumerate (word_list):
                charseq = tuple (item[0])
                word    = string.join (charseq,'')    

                if charseq in self.non_words_set:
                    outfile3.write ('%s\n' %(word))
                    continue    
                
                have_phoneseq = self.word_pronun_table.get (charseq,'')

                if have_phoneseq:
                    WriteOneEntry (outfile1, word, have_phoneseq)
                    num_known_words += 1
                        
                else:
                    production, alignment = self.PredictOneWordPronun (charseq)
                    phoneseq  = []
                        
                    for phonestr in production:
                        phoneseq.extend (phonestr.split())
                    pronunciation = string.join (phoneseq)            
                        
                    if string.find (pronunciation, self.unknown_phone_symbol) == -1:
                        WriteOneEntry (outfile1, word, phoneseq)
                    else:
                        WriteOneEntry (outfile2, word, phoneseq)
                
        outfile1.close()
        if lex_format.lower() != 'festival':
            outfile2.close()
            outfile3.close()

        return num_known_words
    pass


# end class T.
# ------------


