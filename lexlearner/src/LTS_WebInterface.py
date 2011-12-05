# LTS_WebInterface.py                                                 
# ===================                                                 
# 0.01.003  09-Nov-2005  jmk  Renamed from WebLearner to WebInterface.
# 0.01.002  02-Nov-2005  jmk  Added skip and synth buttons.           
# 0.01.001  26-Oct-2005  jmk  Created.                                
# ---------------------                                               
 
import string 
import LatinCharacterSet
import FestivalInterface    
import LTS_RuleLearner
    


# ------------------------------------------------------------------------------------
def WriteHtmlHead(wr):
    wr.write ('<html>\n')
    wr.write ('<body text="#000000" bgcolor="#ccccee">\n')
    wr.write ('<H2> CMU LTS Learner </H2>\n')
    wr.write ('<pre>\n')



# ------------------------------------------------------------------------------------
def WriteHtmlTail(wr):
    wr.write ('\n')
    wr.write ('</pre>  \n')
    wr.write ('</body> \n')
    wr.write ('</html> \n')






# -------------------------------------------------------------------------------------------------
class T (LTS_RuleLearner.T):



    # ---------------------------------------------------------------------------------------------
    def PrepareWebPageWithNewWord (self, writer, given_charseq):
        

        # -----------------------------------------------------------------------------------------
        def WriteRecentWordList(wr):
            wr.write ('<BR><HR>')
            wr.write ('<B>Recent Words:</B> <BR>')
            
            learned_pronuns = self.GetRecentWordPronuns()
            N = len (learned_pronuns)
                
            for i in range (N-1, max(-1,N-11), -1):
                charseq, phoneseq = learned_pronuns[i]
                wr.write ('%4i. %8s  %s\n' %(i+1, string.join(charseq,''), string.join(phoneseq)))
            wr.write ('<BR>')


        # -----------------------------------------------------------------------------------------
        def WriteProductionCounts(wr):
            wr.write ('<B>Production Counts:</B><BR>')
                
            for line in self.GetAllowablesReport():
                wr.write (line)
                wr.write ('<BR>')
            wr.write ('<BR>')


        # -----------------------------------------------------------------------------------------
        def WriteLetterToSoundRules(wr):    
            wr.write ('<B>LTS Rules:</B><BR>')

            lts_rule_system = self.GetRules()
            lhs_symbol_list = lts_rule_system.keys()
            lhs_symbol_list.sort (cmp = LatinCharacterSet.OrderLetters)
            rule_count = 0
            
            for lhs in lhs_symbol_list:
                lts_rule_chain = lts_rule_system[lhs]
                
                for rule_context, rhs_symbol_seq in lts_rule_chain:
                    lhs_symbol  = rule_context[1]
                    context_str = rule_context[0] + '_' + rule_context[2]
                    rhs_string  = string.join (rhs_symbol_seq,'-')
                    if rhs_string == '': rhs_string = ' '
                    rule_count += 1    
                    wr.write ('%4i. %2s -> %5s / %s' %(rule_count, lhs_symbol, rhs_string, context_str))
                wr.write ('<BR>')
            wr.write ('<BR>')


        # -----------------------------------------------------------------------------------------
        def WriteFormComponent (wr):
                
            try:
                next_word_pronun     = self.oracle.GetWordPronunciation (given_charseq)
                next_word_pronun_str = string.join (next_word_pronun)    
            except AttributeError:
                next_word_pronun     = []
                next_word_pronun_str = ''
                            
            next_word_str        = string.join (given_charseq,'')
            predicted_pronun, pa = self.PredictOneWordPronun (given_charseq)
            predicted_pronun_str = string.strip (string.join (predicted_pronun))
            predicted_pronun_lst = string.split (predicted_pronun_str)
                    
            experimental_pronun     = self.GetExperimentalPronunciation (given_charseq)
            experimental_pronun_str = string.join (map ((lambda x: string.join(x)), experimental_pronun))

            wr.write ('<B> Current Word: </B> %s' %(next_word_str))
            wr.write ('<form  action="/internal/skip/">     ')
            wr.write ('<input type=submit value="Skip"> ')
            wr.write ('</form>')
            
            wavefile_pathname = FestivalInterface.SynthesizePhoneSeq (next_word_pronun)
                
            wr.write ('<B> Dictionary Pronunciation: </B><BR>')    
            wr.write ('<form  action="/internal/cheat/">     ')
            wr.write ('<input type=submit value="Cheat" id="b1"> ')
            wr.write ('<input type=text size=20 maxlength=80 name="phoneseq" value="%s" readonly>' %(next_word_pronun_str))
            wr.write ('<input type=hidden name="charseq"  value="%s">' %(next_word_str))
            wr.write ('<a href="%s">  Hear word</a>' %(wavefile_pathname))
            wr.write ('</form>')
                
            wavefile_pathname = FestivalInterface.SynthesizePhoneSeq (predicted_pronun_lst)
                
            wr.write ('<B> Candidate Pronunciations: </B><BR>')    
            wr.write ('<form  action="/internal/select/">     ')
            wr.write ('<input type=submit value="Select" id="b2"> ')
            wr.write ('<input type=text size=20 maxlength=80 name="phoneseq" value="%s" readonly>' %(predicted_pronun_str))
            wr.write ('<input type=hidden name="charseq"  value="%s">' %(next_word_str))
            wr.write ('<a href="%s">  Hear word</a>' %(wavefile_pathname))
            wr.write ('</form>')
                

            wr.write ('<B> Write-in Pronunciation: </B><BR>')  
                
            if experimental_pronun:      
                wavefile_pathname = FestivalInterface.SynthesizePhoneSeq (experimental_pronun)
                wr.write ('<form action="/internal/submit/">     ')
                wr.write ('<input type=submit value="Submit"> ')
                wr.write ('<input type=text size=20 maxlength=80 name="phoneseq" value="%s">' %(experimental_pronun_str))
                wr.write ('<input type=hidden name="charseq"  value="%s">' %(next_word_str))
                wr.write ('<a href="%s">  Hear word</a>' %(wavefile_pathname))
                wr.write ('</form>')
            else:
                wr.write ('<form action="/internal/synth/">     ')
                wr.write ('<input type=submit value="Synth"> ')
                wr.write ('<input type=text size=20 maxlength=80 name="phoneseq" value="%s">' %(experimental_pronun_str))
                wr.write ('<input type=hidden name="charseq"  value="%s">' %(next_word_str))
                wr.write ('</form>')
                    
        pass          


        # Method mainline.
        # ----------------
            
        WriteHtmlHead           (writer)
        WriteFormComponent      (writer)
        WriteRecentWordList     (writer)
        #WriteLetterToSoundRules (writer)
        #WriteProductionCounts   (writer)
        WriteHtmlTail           (writer)
    pass
        


    # ---------------------------------------------------------------------------------------------
    def ProvidePronunciationOracle (self, given_oracle):
        self.oracle = given_oracle
            
    

# end class.
# ----------
