# lts_learner_command.py                                                                           
# ======================                                                                           
# 0.01.002  17-Nov-2005  jmk  Removed configuration files that maps project name to ip port number.
# 0.01.001  10-Nov-2005  jmk  Created.                                                             
# --------------------------                                                                       

import codecs
import getopt
import socket
import string
import StringIO    
import sys
import xmlrpclib
        
import DictionaryIO
import LTS_RuleLearnerSrvr
        

# --------------------------------------------------------------------------------------------------
def ProcessOneCommand (lts_learner, option_table):
    
    method_name = option_table ['--method']
         
        
    if method_name == 'Shutdown':
        try:
            answer = lts_learner.Shutdown()
        except:
            answer = 'bye'
            
    elif method_name == 'GetWorkingDirectory':
        answer = lts_learner.GetWorkingDirectory()
            
    elif method_name == 'GetServerIdentification':
        answer = lts_learner.GetServerIdentification()
            
    elif method_name == 'SetServerIdentification':
        word   = option_table.get ('--word','')
        answer = lts_learner.SetServerIdentification (word)

    elif method_name == 'NumberWordsCovered':
        answer = lts_learner.NumberWordsCovered()

    elif method_name == 'NumberWordsInCorpus':
        answer = lts_learner.NumberWordsInCorpus()
            
    elif method_name == 'PriorityWordsCovered':
        answer = lts_learner.PriorityWordsCovered()

    elif method_name == 'NumberPriorityWords':
        answer = lts_learner.NumberPriorityWords()
            
    elif method_name == 'GetNextWord':
        answer = lts_learner.GetNextWord()
        
        print len(answer), type(answer)
        for i in range(len(answer)):
            val = ord(answer[i])    
            print '%4i %6i %6x' %(i,val,val)
        return        
        
    elif method_name == 'GetNextWordRemove':
        answer = lts_learner.GetNextWordRemove()
              
    elif method_name == 'Get_LTS_Rules':
        answer = lts_learner.Get_LTS_Rules()

    elif method_name == 'GetRecentWordPronuns':
        max_num = int (option_table.get ('--max_number', 1))
        answer  = lts_learner.GetRecentWordPronuns (max_num)
            
    elif method_name == 'SubmitPronunciation':
        word   = option_table ['--word']
        pronun = option_table ['--pronun']
        answer = lts_learner.SubmitPronunciation (word, pronun)

    elif method_name == 'RemoveFromLexicon':
        word   = option_table ['--word']
        answer = lts_learner.RemoveFromLexicon (word)    
            
    elif method_name == 'PredictOneWord':
        word    = option_table ['--word']
        max_num = int (option_table.get ('--max_number', 1))
        answer  = lts_learner.PredictOneWord (word, max_num)
            
    elif method_name == 'WriteOutLexicon':
        if option_table.has_key('--filename'):
            answer = lts_learner.WriteOutLexicon ('Janus', option_table['--filename'])
        else:    
            answer = lts_learner.WriteOutLexicon()

    elif method_name == 'PercentFinished':
        answer = lts_learner.PercentFinished()
            
    elif method_name == 'SynthesizeWord':
        word   = option_table ['--word']
        answer = lts_learner.SynthesizeWord (word, 'test')
            
    elif method_name == 'SynthesizePhoneSeq':
        pronun = option_table ['--pronun']
        answer = lts_learner.SynthesizeWord (pronun, 'test')
               
    else:
        answer = 'Unknown method name: %s' %(method_name)

    
    if '--outfile' in option_table:
        outfile = codecs.open (option_table['--outfile'], 'a', 'utf-8')
        outfile.write ('%s: %s\n' %(method_name, answer))
    else:        
        print '%s: %s' %(method_name, answer)
pass
    


# --------------------------------------------------------------------------------------------------
def ProcessBatchFile (option_table):
            
    word_list = []

    if option_table.has_key ('--festdict'):
        lexicon_file = option_table['--festdict']
        word_list = DictionaryIO.ReadFestivalDictionary (lexicon_file, words_only=False)
            
    elif option_table.has_key ('--lexlist'):
        lexicon_file = option_table['--lexlist']
        word_list = DictionaryIO.ReadLexiconFileWithCounts (lexicon_file, words_only=False)
    

    lts_learner = LTS_RuleLearnerSrvr.T (word_list)
    lts_learner.ConfigurePhoneNames ('CmapFile.txt')    


    batch_file  = file (option_table['--batchfile'],'r')
        
    for rawline in batch_file.readlines():
        line = string.strip (rawline)
        if not line or line[0] == '#': continue    

        pos = string.find (line, '--method')    
        if pos > -1: 
            input_list = []
            for item in string.split (line[pos:], '--'):
                fields = string.split(item, maxsplit=1)
                if len(fields) == 1:
                    input_list.append ('--'+fields[0].strip())
                elif len(fields) == 2:
                    input_list.append ('--'+fields[0].strip())
                    input_list.append (string.replace (fields[1].strip(), '"', ''))

            opt_list, prog_args = getopt.getopt (input_list, '', possible_flags)
            option_table = dict (opt_list)    
            
            ProcessOneCommand (lts_learner, option_table)

    batch_file.close()
pass
    


# --------------------------------------------------------------------------------------------------
# If I'm processing non-ascii 8-bit western character sets, I can use this:                         
# lts_learner_srvr = xmlrpclib.Server ('http://localhost:%s' %(port_number), encoding='ISO-8859-1') 
    
def ProcessCommandLine (option_list, option_table):
    
    # 1. check for the mandatory flags
    if not '--port' in option_list:
        sys.exit ('=nError: no port number specified\n')
            
    elif not '--method' in option_list:
        sys.exit ('\nError: no method call specified\n')


    # 2. get the port number and create a server proxy object
    port_number = int (option_table.get ('--port', 8000))

    lts_learner_srvr = xmlrpclib.Server ('http://localhost:%s' %(port_number), encoding = 'utf-8')
    #lts_learner_srvr = xmlrpclib.Server ('http://localhost:%s' %(port_number), encoding = 'iso8859')


    # 3. process the command line
    try:
        ProcessOneCommand (lts_learner_srvr, option_table)
            
    except socket.error, msg:
        sys.exit ('\nError: %s to port %s\n' %(msg, port_number))
            
    except KeyError, msg:
        sys.exit ('\nError: %s parameter not specified\n' %(msg))
    
    # this results after asking the server to shutdown
    except xmlrpclib.ProtocolError, msg:
        pass

pass
    



# ==============
# Mainline code.
# ==============

if __name__ == '__main__':
        
    possible_flags = \
        ['port=', 'method=', 'word=', 'pronun=', 
         'max_number=', 'filename=', 'batchfile=', 
         'festdict=', 'lexlist=', 
         'outfile=']
        
    try:
        opt_list, prog_args = getopt.getopt (sys.argv[1:], '', possible_flags)
    except getopt.GetoptError, msg:
        sys.exit ('\nGetopt Error: %s\n' %(msg))            
        
    option_table = dict (opt_list)
    option_list  = option_table.keys()   


    if '--batchfile' in option_list:
        ProcessBatchFile (option_table)
    else:
        ProcessCommandLine (option_list, option_table)
