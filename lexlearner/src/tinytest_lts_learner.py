# tinytest_lts_learner.py                                                       
# =======================                                                       
# 0.01.001  15-Mar-2007  jmk  Spun off from the more involved test_lts_learner. 
# ---------------------                                                         

import codecs 
import getopt, os
import string, sys
import socket
import xmlrpclib
     
import DictionaryIO    
import PronunciationOracle 
import WordSelector       
import LTS_IO
import LTS_RuleSystemTrain as LTS



# --------------------------------------------------------------------------------------------------
def WordFreqCompare (item1, item2):
    word1, pron1, freq1 = item1
    word2, pron2, freq2 = item2
        
    if   freq1 < freq2: return +1
    elif freq1 > freq2: return -1
    else:
        return word1 < word2



# --------------------------------------------------------------------------------------------------
def ReadDictionary (festdict_pathname='', lexlist_pathname=''):

    dict_basename = ''
    word_pronun_list_A = []
    word_pronun_list_B = []
        
    if os.path.exists (festdict_pathname) and os.path.isfile (festdict_pathname):
        word_pronun_list_A = DictionaryIO.ReadFestivalDictionary (festdict_pathname, character_encoding='utf-8')
            
        dict_basename = os.path.splitext (os.path.split (festdict_pathname)[1])[0]
        print 'Reading dictionary %s  %i\n' %(festdict_pathname, len(word_pronun_list_A))
            
    if os.path.exists (lexlist_pathname) and os.path.isfile (lexlist_pathname):
        word_pronun_list_B = DictionaryIO.ReadLexiconFileWithCounts (lexlist_pathname)
            
        dict_basename = os.path.splitext (os.path.split (lexlist_pathname)[1])[0]
        print 'Reading word count lexicon %s  %i\n' %(lexlist_pathname, len(word_pronun_list_B))


    result = []

    if word_pronun_list_A and word_pronun_list_B:            
        word_counts_tbl = {}
        word_pronun_tbl = {}

        for word, pronun, ignore in word_pronun_list_A:
            word_pronun_tbl [word] = pronun
                
        for word, ignore, count in word_pronun_list_B:
            word_counts_tbl [word] = count
                 
        for charseq, pronun, fake_count in word_pronun_list_A:
            word = ''.join(charseq)
            word_count = word_counts_tbl.get (word, fake_count)
            result.append ([word, pronun, word_count])
                
        for word, fake_pronun, word_count in word_pronun_list_B:
            if word not in word_pronun_tbl:
                result.append ([word, fake_pronun, 0])    
                
    elif word_pronun_list_A:
        result = word_pronun_list_A
            
    elif word_pronun_list_B:
        result = word_pronun_list_B

    return result, dict_basename
pass
            
 
    
# --------------------------------------------------------------------------------------------------
def TestRuleLearnerSrvr (file_basename, word_order='asis', num_words_to_use=10, verbose=True):

    
    # ------------------------------------------------------------------------------------
    def PrintOutWordPronun (iter_count, word, pronun, word_count=1):
        
        char_val_lst = map ((lambda ch: ord(ch)), word)
            
        if len(char_val_lst) > 0:
            max_char_val = max (char_val_lst)
        else:
            max_char_val = 0        
        
        # case 1. word is in utf-8              
        # case 2. word is ascii or maybe latin-1
            
        if verbose:
            if max_char_val > 255:
                print '%5i %5i TestRuleLearnerSrvr: %24s <- %s' %(iter_count, word_count, pronun, char_val_lst)
            else:        
                print '%5i %5i TestRuleLearnerSrvr: %24s -> %s' %(iter_count, word_count, word, pronun)
    pass              


    N = min (num_words_to_use, len(word_pronun_list))
        

    # Two choices for for submitting words  
    #   a) use the WordSelector object, or  
    #   b) take from the list in order      
        
    if word_order in ['asis', 'freq']:
        if word_order == 'freq':
            word_pronun_list.sort (cmp = WordFreqCompare)
                
        for i in range(N):
            charseq, phoneseq, count = word_pronun_list[i]
            w1 = string.join (charseq,'')
            p1 = string.join (phoneseq, ' ')
            PrintOutWordPronun (i+1, w1, p1, count)
            if w1 and p1:    
                lts_learner.SubmitPronunciation (w1, p1)            # call for LTS_RuleLearnerSrvr.T object
               #lts_learner.SubmitPronunciation (charseq, phoneseq) # call for LTS_RuleLearner.T object    
        if verbose: print    
    elif word_order == 'select':
        for i in range(N):
            w1 = lts_learner.GetNextWord()
            p1 = string.join (dict_oracle.GetWordPronunciation (w1))
            if w1 and p1:    
                PrintOutWordPronun (i+1, w1, p1)
                lts_learner.SubmitPronunciation (w1, p1)
        if verbose: print

    # write out some resulting files
    if verbose:    
        print 'Writing LTS rules to %s\n' %('tinytest.lts_rules')
        
    lts_learner.WriteOutRules           ('%s.%s' %(file_basename, 'lts_rules.lst'))
    lts_learner.PickleStateInfoRules    ('%s.%s' %(file_basename, 'lts_rules.pkl'))
    lts_learner.WriteAllowablesFile     ('%s.%s' %(file_basename, 'allowables.scm'))
    lts_learner.WriteProductionsSummary ('%s.%s' %(file_basename, 'productions.lst'))
    lts_learner.WriteOutFestivalRules   ('%s.%s' %(file_basename, 'lexrules.scm'))
        
    lts_learner.WriteOutLexicon ('Festival', '%s.%s' %(file_basename, 'lexicon.festival'))
    lts_learner.WriteOutLexicon ('Janus',    '%s.%s' %(file_basename, 'lexicon.janus'))
    lts_learner.WriteOutLexicon ('Sphinx',   '%s.%s' %(file_basename, 'lexicon.sphinx'))

    for i in range(N):
        charseq, phoneseq, ignore = word_pronun_list[i]
        word = string.join (charseq,'')
        p1 = string.join (phoneseq, ' ')
        p2 = lts_learner.PredictOneWord (word,1)
        if verbose: print '%4i word, pred, ref: %16s %24s  %s' %(i+1, word, p2, p1)
    if verbose: print


pass

# ----------------------------------------------------------------------------------------------
# Some example usages:                                                                          
# 1. tinytest_lts_learner.py --dict ../dicts/hindi_lexicon.scm --numwords 20                    
# 2. tinytest_lts_learner.py --dict ../dicts/festdict-0.7a.4k_sample --numwords 25              
# 3. tinytest_lts_learner.py --dict ../dicts/festdict-0.7a.4k_sample --numwords 15 --port 8001  
# 4. tinytest_lts_learner.py --port 8001 --shutdown                                             
# ----------------------------------------------------------------------------------------------
        
if __name__ == '__main__':
        
    flag_list = [ \
        'shutdown',             # shut down the server, --port must be provided             
        'port=',                # if specified communicate with with a server on this port  
        'dict=',                # a pronunciation dictionary in festival format             
        'lexlist=',             # a lexicon with word frequency counts                      
        'numwords=',            # number of words to read from lexicon/dictionary           
        'phoneset=',            # filename containing list of phonemes, one per line        
        'allowables=',          # filename containing default pronunciations of each letter 
        'wordorder=',           # order that words are learned: asis, freq, select          
        ]
    
    try:
        opt_list, prog_args = getopt.getopt (sys.argv[1:], '', flag_list)
        option_tbl = dict (opt_list)
    except getopt.GetoptError, msg:
        print 'Error: %s\n' %(msg)
        sys.exit()
            

    # establish a default value of numwords
    if not '--numwords' in option_tbl:
        option_tbl ['--numwords'] = 10
            

    # First test if a server shutdown is being requested.

    if '--shutdown' in option_tbl and '--port' in option_tbl:
        try:
            port_number_str = option_tbl['--port']
            lts_learner = xmlrpclib.Server ('http://localhost:%s' %(port_number_str), encoding = 'utf-8')
            lts_learner.GetNumberOfRules()
            lts_learner.Shutdown()
                
        except xmlrpclib.ProtocolError, msg:
            print 'Shutting down server on port %s' %(port_number_str)
                
        except socket.error, msg:
            print 'Error: %s to port %s' %(msg, port_number_str)
        sys.exit()    


    # --dict option    read in a festival pronuncation dictionary
    # --lexlist option read in a lexicon with word counts        
    # Todo: combine two files so that word freqs are incorporated
        
    dict_pathname = option_tbl.get ('--dict','')
    #list_pathname = option_tbl.get ('--lexlist','')
    word_pronun_list, dict_basename = ReadDictionary (dict_pathname, '')
   #word_pronun_list, dict_basename = ReadDictionary (dict_pathname, list_pathname)

    
    unknown_wordlist = []
    #infile = codecs.open (list_pathname,'r','utf-8')
        
    #for rawline in infile.readlines(): 
    #    line = rawline.strip()
    #    unknown_wordlist.append ((line,'',1))
    #infile.close()        

    # Either context the LTS learner or create a local version, then run the test.
            
    if '--numwords' in option_tbl:
        import LTS_RuleLearnerSrvr

        # case 1.  connect to a running server
        if '--port' in option_tbl:
               
            port_number_str = option_tbl['--port']
                
            try:
                lts_learner = xmlrpclib.Server ('http://localhost:%s' %(port_number_str), encoding = 'utf-8')
            except socket.error, msg:
                print 'Error: %s to port %s' %(msg, port_number_str)
                sys.exit()    
                    
        # case 2. run a local LTS learner
        else:
            lts_learner = LTS_RuleLearnerSrvr.T (word_pronun_list, unknown_wordlist, unknown_phone_symbol='*')

        
        if '--phoneset' in option_tbl:
            phoneme_pathname = option_tbl['--phoneset']
            if os.path.exists (phoneme_pathname) and os.path.isfile (phoneme_pathname):
                lts_learner.DisguisePhonemeNames (phoneme_pathname)
                 
        if '--allowables' in option_tbl:
            primer_pathname = option_tbl['--allowables']
            if os.path.exists (primer_pathname) and os.path.isfile (primer_pathname):
                lts_learner.PrimeWithAllowables (primer_pathname)
        
        
        # now test the LTS learner
        N = int (option_tbl.get('--numwords',1))
        word_order = option_tbl.get('--wordorder','asis')    
            
        print 'num words - training, testing: %i %i' %(len(word_pronun_list), len(unknown_wordlist))
            
        lts_learner.PrimeWithPronunciations (word_pronun_list[:N])
       #lts_learner.WriteOutLexicon ('Festival', os.path.join('.','dictionary-festival'))
        lts_learner.WriteOutLexicon ('Janus',    os.path.join('.','dictionary-janus'))
        lts_learner.WriteOutRules   ('dictionary.lts')


        #dict_oracle = PronunciationOracle.T (word_pronun_list, disguise_phone_names = True)
        #TestRuleLearnerSrvr (dict_basename, word_order, num_words_to_use=N, verbose=True)
        

print '\n%s: very end' %(sys.argv[0])

