# WordSelector.py                                                                   
#================                                                                   
# 0.01.001  12-Apr-2007  jmk  Created. Selects words based on occurance frequency.  
# ---------------------                                                             

import string
import sys
import Logger    
import SimpleWordSelector
    

class T(SimpleWordSelector.T):
    

    # ----------------------------------------------------------------------------------------------
    def __init__(self, priority_word_list, secondary_word_list):
        self.textlog.write (Logger.GetFunctionName(__name__))
        
        combined_word_list = []
        self.priority_word_set = set() 

        for item in priority_word_list:
            word, pronun, count = item
            self.priority_word_set.add(word)
            combined_word_list.append(item)
                
        for item in secondary_word_list:
            word = item[0]
            if word not in self.priority_word_set:
                combined_word_list.append(item)

        SimpleWordSelector.T.__init__(self,combined_word_list)
            
        self.priority_active_wordset = set()
        self.priority_completed_wordset = set()
            
        for word, pronun, count in self.active_wordlist:
            if word in self.priority_word_set:
                self.priority_active_wordset.add(word)
                    
        for word, pronun, count in self.completed_wordlist:
            if word in self.priority_word_set:
                self.priority_completed_wordset.add(word)
                    

    # ----------------------------------------------------------------------------------------------
    def PriorityWordsCovered (self):
        self.textlog.write (Logger.GetFunctionName(__name__))
        return len(self.priority_completed_wordset)
            
    def NumberPriorityWords (self):
        self.textlog.write (Logger.GetFunctionName(__name__))
        return len(self.priority_completed_wordset) + len(self.priority_active_wordset)

    def PercentPriorityWordsCovered (self):
        self.textlog.write (Logger.GetFunctionName(__name__))
        a = len (self.priority_completed_wordset)
        b = len (self.priority_active_wordset)
        return 100.0 * float(a) / max(1,float(a+b))


    # ----------------------------------------------------------------------------------------------
    def HappyWithWord (self, given_word):
        self.textlog.write (Logger.GetFunctionName(__name__))
        if given_word in self.priority_word_set:
            self.priority_completed_wordset.add (given_word)
            self.priority_active_wordset.remove (given_word)    
        SimpleWordSelector.T.HappyWithWord (self,given_word)
    
            
    # ----------------------------------------------------------------------------------------------
    def UnhappyWithWord (self, given_word):
        self.textlog.write (Logger.GetFunctionName(__name__))
        if given_word in self.priority_word_set:
            self.priority_active_wordset.remove (given_word)    
        SimpleWordSelector.T.UnhappyWithWord (self,given_word)
    
 
# end class
# =========
