# WordSelector.py                                                                   
#================                                                                   
# 0.01.001  12-Apr-2007  jmk  Created. Selects words based on occurance frequency.  
# ---------------------                                                             

import codecs
import string
import sys
import Logger


# --------------------------------------------------------------------------------------------------
def IsJunkWord (given_word):
    all_chars_uninteresting = True
        
    for ch in given_word:
        if not (ch in string.punctuation or ch in string.digits or ch in string.whitespace):
            all_chars_uninteresting = False
    return all_chars_uninteresting    

    

# --------------------------------------------------------------------------------------------------
class T(object):
 
    
    # ----------------------------------------------------------------------------------------------
    # Input: given_word_list is assumed to be sorted from most frequent to least frequent.          
    #
    def __init__ (self, given_word_list):
        
        self.junk_wordlist = []
        self.active_wordlist = []
        self.completed_wordlist = []    

        # Reverse because we want to make use of the O(1) pop() operation in HappyWithWord. 
        # That is, the end of active_wordlist will be the most frequent word.               
        given_word_list.reverse()

        for item in given_word_list:
            word, pronun, count = item
                
            if IsJunkWord(word):
                self.junk_wordlist.append(item)
            elif pronun:
                self.completed_wordlist.append(item)
            else:
                self.active_wordlist.append(item)        
                    
        self.active_list_index = len(self.active_wordlist) - 1
            

    # ----------------------------------------------------------------------------------------------
    def NumberWordsCovered (self):
        self.textlog.write (Logger.GetFunctionName(__name__))
        return len(self.completed_wordlist)
            
    def NumberWordsInCorpus (self):
        self.textlog.write (Logger.GetFunctionName(__name__))
        return len(self.completed_wordlist) + len(self.active_wordlist)

    def PercentWordsCovered (self):
        self.textlog.write (Logger.GetFunctionName(__name__))
        a = len (self.completed_wordlist)
        b = len (self.active_wordlist)
        return 100.0 * float(a) / max(1,float(a+b))

    def PercentTokensCovered (self):
        self.textlog.write (Logger.GetFunctionName(__name__))
        a = sum (map ((lambda x: x[2]), self.completed_wordlist))
        b = sum (map ((lambda x: x[2]), self.active_wordlist))
        return 100.0 * float(a) / max(1,float(a+b))


    # ----------------------------------------------------------------------------------------------
    def _RemoveCurrentWord (self, destination_list=None):
        self.textlog.write (Logger.GetFunctionName(__name__))
        
        def minmax (value, maxval, minval=0): 
            return min(maxval,max(minval,value))
            
        N = len (self.active_wordlist)
        if N > 0:    
            i = minmax (self.active_list_index,N-1)
            if destination_list != None:
                item = self.active_wordlist.pop(i)
                destination_list.append(item)
            N = len (self.active_wordlist)
        if N > 0:        
            self.active_list_index = (i-1) % N
        else:
            self.active_list_index = 0        
        return N


    # ----------------------------------------------------------------------------------------------
    def HappyWithWord (self, given_word):
        self.textlog.write (Logger.GetFunctionName(__name__))
        return self._RemoveCurrentWord (self.completed_wordlist)
    
            
    # ----------------------------------------------------------------------------------------------
    def UnhappyWithWord (self, given_word):
        self.textlog.write (Logger.GetFunctionName(__name__))
        return self._RemoveCurrentWord (self.junk_wordlist)
    
            
    # ----------------------------------------------------------------------------------------------
    def SkipCurrentWord (self, given_word):
        self.textlog.write (Logger.GetFunctionName(__name__))
        return self._RemoveCurrentWord()
         
          
    # ----------------------------------------------------------------------------------------------
    # Note: Used to allow IndexError to be raised when we reach the end of the list.                
    #       Now I return the empty string as an end of list indicator                               
    #                                                                                               
    def GetNextWord (self, word_as_charseq=False, verbose=False):
        self.textlog.write (Logger.GetFunctionName(__name__))
            
        N = len (self.active_wordlist)
        if N == 0:
            return ''
        else:
            i = self.active_list_index % N
            return self.active_wordlist[i][0]
            

# end SimpleWordSelector.T
# ------------------------
    



# ==============
# Mainline code.
# ==============
    
if __name__ == '__main__':
    import sys
    import DictionaryIO    
            
    lexicon_pathname = sys.argv[1]
        
    if len (sys.argv) > 2:
        outfile = codecs.open (sys.argv[2], 'w', 'utf-8')
    else:
        outfile = sys.stdout        

    word_list = DictionaryIO.ReadLexiconFileWithCounts (lexicon_pathname, words_only=False, sorted_by_count=True)
    selector  = T (word_list)
    loop_cnt  = 0    

    try:
        while True:
            loop_cnt += 1    
            charseq, ngram, score = selector.GetNextWord(False)
            selector.HappyWithWord (charseq)
            ngram_str = string.join (ngram,'')
            word = string.join (charseq,'')
            percent_completed = selector.PercentFinished()
                
            outfile.write ('%4i %6i %3s %5.2f  %s\n' %(loop_cnt, score, ngram_str, percent_completed, word))
    except IndexError, msg:
        print msg

        

