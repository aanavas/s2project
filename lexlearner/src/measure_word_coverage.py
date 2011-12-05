# measure_word_coverage.py              
# ========================              
# 0.01.001  06-May-2007  jmk  Created.  
# ------------------------------------  

import codecs
import getopt
import os, sys
import string
import DictionaryIO
import PathConfig    
import PromptFileIO

from Column import column
    
    
            

# ==============                                            
# Mainline code.                                            
# ==============                                            
# Example usage:                                            
#   py measure_word_coverage.py \                           
#       --wfreq   ../test/Konkani/konkani_sharath.wfreq \   
#       --pronun  ../test/Konkani/konkani_sharath.pronuns \ 
#       --prompts ../test/Konkani/konkani_sharath.prompts   

if __name__ == '__main__':
    
    flag_list = ['wfreq=', 'pronun=', 'prompts=']

    try:
        opt_list, prog_args = getopt.getopt (sys.argv[1:], '', flag_list)
        option_tbl = dict (opt_list)
    except getopt.GetoptError, msg:
        print 'Error', msg
        sys.exit('      type --help for program options\n')


    prompt_file_pathname = option_tbl.get ('--prompts','')
    pronun_file_pathname = option_tbl.get ('--pronun','')
    wfreq_file_pathname  = option_tbl.get ('--wfreq','')

    for pathname in [prompt_file_pathname, pronun_file_pathname, wfreq_file_pathname]:
        print 'Reading %s' %(pathname)
    print        


    word_freq_list      = DictionaryIO.ReadLexiconFileWithCounts (wfreq_file_pathname, sorted_by_count=True)
    words_with_pronuns  = DictionaryIO.ReadFestivalDictionary (pronun_file_pathname, words_only=True)
    recorded_prompt_tbl = PromptFileIO.Read (prompt_file_pathname)

    word_pronun_counts = {}
    for word, ignore, count in word_freq_list:
        if word in words_with_pronuns:
            word_pronun_counts [word] = count
        

    prompt_tokens_covered = 0
    total_prompt_tokens = 0
    total_prompt_words = set()    
    uncovered_words = {}    

    for prompt_name, prompt in sorted (recorded_prompt_tbl.items()):
        word_list = prompt.split()
        total_prompt_tokens += len(word_list)    

        for raw_word in word_list:
            word = DictionaryIO.TrimExternalPunctuation (raw_word).lower()
            total_prompt_words.add (word)    

            if word in words_with_pronuns:
                prompt_tokens_covered += 1
            else:
                uncovered_words[word] = uncovered_words.get(word,0) + 1
        

    total_token_count    = sum (column (word_freq_list,2))
    covered_prompt_words = len (total_prompt_words) - len (uncovered_words)
    corpus_word_percent  = 100.0 * len(word_pronun_counts) / float (max (1,(len(word_freq_list))))
    corpus_token_percent = 100.0 * sum(word_pronun_counts.values()) / float (max (1,total_token_count))
    prompt_token_percent = 100.0 * prompt_tokens_covered / float (max (1,total_prompt_tokens))
    prompt_word_percent  = 100.0 * covered_prompt_words / float (max (1,len(total_prompt_words)))  

    print '  corpus word coverage: %6i / %-6i (%3.2f)' %(len(word_pronun_counts), len(word_freq_list), corpus_word_percent)
    print ' corpus token coverage: %6i / %-6i (%3.2f)' %(sum(word_pronun_counts.values()), total_token_count, corpus_token_percent) 
    print '  prompt word coverage: %6i / %-6i (%3.2f)' %(covered_prompt_words, len(total_prompt_words), prompt_word_percent)
    print ' prompt token coverage: %6i / %-6i (%3.2f)' %(prompt_tokens_covered, total_prompt_tokens, prompt_token_percent)
    print

    uncovered_word_list = sorted ([(v,k) for k,v in uncovered_words.items()], reverse=True)
    
    """    
    outfile = codecs.open ('uncovered_words.lst', 'w', 'utf-8')
    for cnt, (freq_count, word) in enumerate (uncovered_word_list):
        outfile.write ('%4i %6i  %s\n' %(cnt+1, freq_count, word))
    outfile.close()
    """
        
