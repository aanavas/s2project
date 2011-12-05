# convert_dictionary_format.py                                                  
# ============================                                                  
# 0.01.001  10-Sep-2007  jmk  Created to convert festival to janus dict formats.
# ----------------------------                                                  

import getopt
import os,sys    
import DictionaryIO

from Column import column


# ==============
# Mainline code.
# ==============

if __name__ == '__main__':
    flag_list = [('help',        'this command'),
                 ('festdict=',   'filename of festival-format pronunciation dictionary'),
                 ('janusdict=',  'filename of janus-format pronunciation dictionary')]

    try:
        opt_list, prog_args = getopt.getopt (sys.argv[1:], '', column(flag_list))
        option_tbl = dict (opt_list)
    except getopt.GetoptError, msg:
        print 'Error', msg
        sys.exit('      type --help for program options\n')


    # Print out the options if requested.

    if option_tbl.has_key('--help') or len(sys.argv) == 1:
        print 'python', sys.argv[0]
        for option_flag, description in flag_list:
            print '%12s %s' %(option_flag, description)
        print
        sys.exit()    


    # Read in the festival format dictionary and convert it to janus format.    
    # If the janus output filename is not provided then the festival dictionary 
    # is read in but nothing is done with it.                                   
        
    word_pronun_list = []

    if '--festdict' in option_tbl:
        lexicon_file = option_tbl['--festdict']
            
        if os.path.exists(lexicon_file) and os.path.isfile(lexicon_file):
            word_pronun_list = DictionaryIO.ReadFestivalDictionary (lexicon_file, words_as_charseq=False)
            print 'Reading', lexicon_file
        print '  num words read', len(word_pronun_list)
                
        if '--janusdict' in option_tbl:
            output_file = option_tbl['--janusdict']
            DictionaryIO.WriteJanusDictionary (output_file, word_pronun_list)
            print 'Writing', output_file

