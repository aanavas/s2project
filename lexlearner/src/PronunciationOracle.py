# PronunciationOracle.py
#=======================
# 0.01.001  23-Oct-2005  jmk  Split off from find_lexicon_allowables.
# ---------------------
    
import string
import sys
    
import DictionaryIO
from   Column import column

 

# --------------------------------------------------------------------------------------------------
class T(object):

    
    # ----------------------------------------------------------------------------------------------
    # Comment: I introduced disguise_phone_names because my DTW algorithm called from LTS_Allowables
    #          does not align properly if the characters in the letter set overlap with characters  
    #          in the phoneset.                                                                     
        
    #def __init__ (self, dictionary_pathname, disguise_phone_names = False):
    #    self.word_pronuns_list = DictionaryIO.ReadFestivalDictionary (dictionary_pathname, words_only=False)
                

    def __init__ (self, given_word_pronuns, disguise_phone_names = False):
                
        self.word_pronuns_list = given_word_pronuns[:]
  
        self.pronun_lookup  = {}
        self.unique_letters = set()
        self.unique_phones  = set()
        self.letter_counts  = {}
        self.phone_counts   = {}

        for word, pronun, count in self.word_pronuns_list:
            self.pronun_lookup [tuple(word)] = tuple (pronun)
            self.unique_letters |= set (word)
            self.unique_phones  |= set (pronun)
                
            for ltr in word:   self.letter_counts[ltr] = self.letter_counts.get(ltr,0) + 1
            for phn in pronun: self.phone_counts[phn]  = self.phone_counts.get(phn,0)  + 1
                
        self.inverse_name_table = {}
                         
        if disguise_phone_names:
            phone_list = list (self.unique_phones)
            phone_list.sort()
            phone_trans_tbl = {}
                              
            for i, ph in enumerate (phone_list):
                disguised_name = string.zfill (i+1,2)
                phone_trans_tbl[ph] = disguised_name
                self.inverse_name_table [disguised_name] = ph   
                
            for i, (word, pronun, count) in enumerate (self.word_pronuns_list):
                new_pron = map ((lambda x: phone_trans_tbl[x]), pronun)
                self.word_pronuns_list[i] = (word, new_pron, count)
                    
        else:
            for ph in self.unique_phones:
                self.inverse_name_table[ph] = ph   
                     
        pass
             


    # ----------------------------------------------------------------------------------------------
    def GetFullPronunciationList (self):
        return self.word_pronuns_list


    # ----------------------------------------------------------------------------------------------
    def GetFullWordsOnlyList (self): 
        return column (self.word_pronuns_list)


    # ----------------------------------------------------------------------------------------------
    def GetLettersAndPhoneSets(self):    
        return self.unique_letters, self.unique_phones


    # ----------------------------------------------------------------------------------------------
    def GetLettersAndPhoneCounts(self):    
        return self.letter_counts, self.phone_counts


    # ----------------------------------------------------------------------------------------------
    def GetPhoneNameInversionTable (self):    
        return self.inverse_name_table
 
 
    # ----------------------------------------------------------------------------------------------
    def GetWordPronunciation (self, given_word):
        
        word = tuple (given_word)

        if len(word) > 0 and word[0] == '#':
            answer = self.pronun_lookup.get (word[1:-1], ())
        else:
            answer = self.pronun_lookup.get (word,())
        return answer
    pass                
            
 
# end class T.
# ============
