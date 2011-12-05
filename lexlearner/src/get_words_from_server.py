# get_words_from_server.py
# ========================
# 0.01.001  01-May-2007  jmk  Created for debugging purposes.
    
import codecs
import getopt
import os, sys
import string
import socket
import xmlrpclib
import DictionaryIO
import LTS_RuleLearnerSrvr
     



# ==============
# Mainline code.
# ==============

if __name__ == '__main__':
        
    possible_flags = ['port=', 'numwords=', 'outfile=']
        
    try:
        opt_list, prog_args = getopt.getopt (sys.argv[1:], '', possible_flags)
    except getopt.GetoptError, msg:
        sys.exit ('\nGetopt Error: %s\n' %(msg))            
        
    option_tbl = dict (opt_list)
    port_num   = int (option_tbl.get ('--port',8000))
    num_words  = int (option_tbl.get ('--numwords',10))
    filename   = option_tbl.get ('--outfile','a.out')  


    lts_learner_srvr = xmlrpclib.Server ('http://localhost:%s' %(port_num), encoding = 'utf-8')


    try:
        outfile = codecs.open (filename, 'w', 'utf-8')

        word_list_string = lts_learner_srvr.GetRecentWordPronuns(999999)
        word_list = word_list_string.split('\n')
            
        print '\nSize of word_pronun list: %i' %(len(word_list))
        print 'Writing to %s' %(filename)    

        for i in range(num_words):
            word = lts_learner_srvr.GetNextWord()
            outfile.write ('%6i %s\n' %(i+1, word))    
        outfile.close()        
            
    except socket.error, msg:
        sys.exit ('\nError: %s to port %s\n' %(msg, port_num))
            
    except KeyError, msg:
        sys.exit ('\nError: %s parameter not specified\n' %(msg))
    
    except xmlrpclib.ProtocolError, msg:
        pass


