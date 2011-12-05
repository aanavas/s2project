# DictionaryIO.py                                                                                   
# ===============                                                                                   
# 0.02.002  24-Apr-2007  jmk  ReadLexiconFileWithCounts now by default sorts by word frequency.     
# 0.02.001  14-Mar-2007  jmk  Revised to support utf-8.                                             
# 0.01.005  05-Dec-2006  jmk  Added auto character detection to ReadFestivalDictionary().           
# 0.01.004  17-Nov-2005  jmk  Added ReadLexiconFileWithCounts().                                    
# 0.01.003  23-Oct-2005  jmk  Added WriteWordListGrouped(), WriteWordListHisto().                   
# 0.01.002  23-Oct-2005  jmk  Added SortByWordGroups().                                             
# 0.01.001  13-Oct-2005  jmk  Split off from find_lexicon_allowables.py                             
# ---------------------                                                                             
# Todo: integrate this with the CmuDict module and make the formats consistent.                     
    
 
import codecs
import string, sys
import ConfigPath
import LatinCharacterSet
from   Column import column
    


# --------------------------------------------------------------------------------------------------
# Function: ReadFestivalDictionary.                                                                 
# Purpose:  Convert a dictionary in festival (scheme) format to a simple python format.             
# Params:   dict_pathname       - the dictionary file that is read in                               
#           words_as_charseq    - the default, alternative is as strings                            
#           words_only          - return the word list but not the pronunciations                   
#           reverse_direction   - swap words and pronunciations, for phone to letter rules          
#           character_encoding  - one of 'ascii', 'utf-8', 'auto'                                   
#                                                                                                   
# Output:   A list of [letter-seq, phoneme-seq] pairs with word count in the third position.        
#           example of one entry:  [('a', 'k', 'i', 'v', 'a'), ('A', 'K', 'I', 'V', 'A'), 1]        
#                                                                                                   
# Input:    The general format is (word parts-of-speech pronunciation)                              
#             - the word is either a string or a sequence of characters                             
#             - the part of speech is usually nil, but can be 'n', 'v' etc. This field is ignored.  
#             - the pronunciation is a tuple of phone symbols                                       
#   Case 1. Example when the words are strings:                                                     
#       ("ahora"  nil (a o r a))                                                                    
#       ("ahorra" nil (a o rr a))                                                                   
#       ("ahi"    nil (a i))                                                                        
#       ("akiva"  nil (a k i v a))                                                                  
#   Case 2. Example when the word is given as a list of letters:                                    
#       (("a" "h" "o" "r" "a") nil (a o r a))                                                       
#   The code to distinguish these two cases is based on counting the number of left-parenthesis     
#   and so is not general purpose at all.                                                           


def ReadFestivalDictionary (dict_pathname,
                            words_as_charseq   = False,
                            words_only         = False, 
                            reverse_direction  = False, 
                            character_encoding = 'auto'):
    
    # --------------------------------------------------------------------------
    def DetermineEncoding():

        infile = file (dict_pathname, 'r')
            
        for line in infile:
            for ch in line:
                if ch not in string.printable:
                    infile.close()
                    return 'utf-8'
        return 'ascii'
                        

    if character_encoding == 'auto':
        character_encoding = DetermineEncoding()
        
    if character_encoding != 'ascii':
        dec = codecs.getdecoder (character_encoding)
        enc = codecs.getencoder (character_encoding)
         
    word_pronun_list  = []
    word_pronun_table = {}
    phone_number_tbl  = {}

    char_mapping = string.maketrans ('()"','   ')
         
    infile = file (dict_pathname, 'r')
   #infile = codecs.open (dict_pathname, 'r', 'utf-8')


    for cnt, rawline in enumerate (infile.readlines()):
        line = string.strip (rawline.strip()[1:-1])
        if not line: continue
                
        num_left_parens = line.count('(')
        pronun_part = ''    
            
        # Case 1. the word is given as a string
            
        if num_left_parens == 1:
            quote_pos = string.rfind (line, '"') + 2
            word_part = string.translate (line[:quote_pos], char_mapping)
            rest_part = string.translate (line[quote_pos:], char_mapping)
            fields    = string.split (rest_part, maxsplit=1)
                
            #print cnt+1, len(fields), quote_pos, character_encoding, rest_part
                
            if len(fields) >= 2: 
                if character_encoding == 'ascii':
                     word_letters = list (string.strip(word_part))
                else:    
                    try:
                        word_unicode = dec  (string.strip(word_part))
                        word_letters = list (word_unicode[0])
                        assert len(word_letters) == enc(word_unicode[0])[1]
                    except:
                        #print 'SKIPPING', cnt+1, line
                        continue
                        
                annotation  = fields[0]    
                pronun_part = fields[1]
        
        # Case 2. the word given as a character sequence
        elif num_left_parens == 2:
            pos1 = line.find ('(')
            pos2 = line.find (')')
            pos3 = line.rfind ('(')
            pos4 = line.rfind (')')

            letter_part  = line[pos1:pos2].translate (char_mapping)
            pronun_part  = line[pos3:pos4].translate (char_mapping)
            annotation   = line[pos2-1:pos3-1].strip() 
            word_letters = letter_part.split()
                
        if not pronun_part: continue

        
        # check for duplicates before adding words to the pronunciation list
            
        word_string  = string.join (word_letters,'')
        word_phones  = tuple (pronun_part.split())
        word_letters = tuple (word_letters)
            
        if words_as_charseq:
            word = word_letters
        else:
            word = word_string        

        # This adds a default word count of 1, and allows only unique words
        

        if not word_pronun_table.has_key(word):
            if not reverse_direction:
                word_pronun_list.append ([word, word_phones, 1])
            else:
                word_pronun_list.append ([word_phones, word, 1])
            word_pronun_table [word] = True
        
        """            
        if not reverse_direction:
            word_pronun_list.append ([word_letters, word_phones, annotation])
        else:
            word_pronun_list.append ([word_phones, word_letters, annotation])
        """
                
    infile.close()


    if words_only:
        return column (word_pronun_list, 0)
    else:        
        return word_pronun_list            
pass        



# --------------------------------------------------------------------------------------------------
def WriteFestivalDictionary (dict_pathname, word_pronun_list, phone_name_translation_table = {}):
    
   #outfile = file (dict_pathname, 'w')
    outfile = codecs.open (dict_pathname, 'w', 'utf-8')


    for charseq, phoneseq, count in word_pronun_list:
        word = string.join (charseq,'')
        pronun_lst = map ((lambda x: phone_name_translation_table.get(x,x)), phoneseq)
        pronun_str = string.join (pronun_lst,' ')
        outfile.write ('("%s" %i (%s))\n' %(word, count, pronun_str))
       #outfile.write ('("%s" nil (%s))\n' %(word, pronun_str))
    outfile.close()
pass
    


# --------------------------------------------------------------------------------------------------
def WriteJanusDictionary (dict_pathname, word_pronun_list, phone_name_translation_table = {}):
    
    # ------------------------------------------------------------------------------------------
    def WriteOneEntry (word, phoneseq):
        
        pronun = string.join (phoneseq)
        
        outfile.write ('%-24s ' %(word))
            
        if len(phoneseq) == 0:
            outfile.write ('{}\n')
        else:
            outfile.write ('{{%s WB}' %(phoneseq[0]))
                
            for ph in phoneseq[1:-1]:
                outfile.write (' %s' %(ph))
                    
            if len(phoneseq) >= 2:
                outfile.write (' {%s WB}' %(phoneseq[-1]))
            outfile.write('}\n')



   #outfile = file (dict_pathname, 'w')
    outfile = codecs.open (dict_pathname, 'w', 'utf-8')


    for charseq, phoneseq, count in word_pronun_list:
        word = string.join (charseq,'')
        pronun_lst = map ((lambda x: phone_name_translation_table.get(x,x)), phoneseq)
        pronun_str = string.join (pronun_lst,' ')
        WriteOneEntry (word, pronun_lst)
    outfile.close()
pass
    


# --------------------------------------------------------------------------------------------------
def TrimExternalPunctuation (given_word, punctuation_chars = string.punctuation):
    
    L = len (given_word)
    beg = 0
    end = L
        
    for i in range(L):
        if given_word[i] not in punctuation_chars:
            break
        beg += 1        
            
    for i in range(L-1,-1,-1):
        if given_word[i] not in punctuation_chars:
            break
        end -= 1        
             
    return given_word [beg:end]
pass        

             
        
# --------------------------------------------------------------------------------------------------
# Returns:  Either a word list (word_only=True) or a word_pronun_count list.                        
#           Format: list of (word, pronunciation, count) tuples.                                    
# Note:     The pronunciation will not be known, only the word frequency count                      
    
def ReadLexiconFileWithCounts (dict_pathname, words_only=False, sorted_by_count=True):
    

    def ReadFile (infile):
        for cnt, rawline in enumerate (infile.readlines()):
            line = rawline.strip()
            if not line: continue
            fields = string.split (line, maxsplit=2)
                
            if len(fields) == 2:
                word  = TrimExternalPunctuation (fields[0])
                count = int (fields[1])
                if word:    
                    word_freq_table[word] = word_freq_table.get(word,0) + count
        

    print 'ReadLexiconFileWithCounts', dict_pathname, '\n'
    
    # Read in the word freq file and accumulate counts for each word        
    # Use a table rather than a list in case a word appears more than once. 
        
    word_freq_table = {}

    try:
        infile = codecs.open (dict_pathname, 'r', 'utf-8')
        ReadFile (infile)
    except UnicodeDecodeError, msg:
        print 'Warning: %s is not a utf-8 file, trying again as iso-8859' %(dict_pathname)
        infile.close()
        infile = codecs.open (dict_pathname, 'r', 'iso8859')
        ReadFile (infile)    
    infile.close()
        
    # convert the word count table to a list
                
    word_freq_list = []
    for word in sorted (word_freq_table):
        word_freq_list.append ([word, '', word_freq_table[word]])

    # then either extract only the words or sort the contents by frequency

    if words_only:
        return column (word_freq_list, 0)
            
    elif sorted_by_count:
        sorted_by_count = sorted ([(v, k) for k, v in word_freq_table.items()], reverse=True)
        sorted_by_count = [[v, '', k] for k, v in sorted_by_count]
        return sorted_by_count
            
    else:        
        return word_freq_list            

pass


# --------------------------------------------------------------------------------------------------



# --------------------------------------------------------------------------------------------------
# Example ordering with Pivot_Val set to ...                                                        
#   0: [(2, 0), (2, 1), (2, -1), (3, 0), (3, 1), (3, -1), (4, 0), (4, 1), (5, 0)]                   
#   3: [(3, 0), (3, 1), (3, -1), (2, 0), (2, 1), (2, -1), (4, 0), (4, 1), (5, 0)]                   
     
Pivot_Val = 3
    
def ComparePairKeys (item1, item2):
    
    num_chars1, symbol_diff1 = item1
    num_chars2, symbol_diff2 = item2
        
    sort_factor1 = abs (num_chars1 - Pivot_Val)
    sort_factor2 = abs (num_chars2 - Pivot_Val)
          
    if   sort_factor1 < sort_factor2:           return -1 
    elif sort_factor1 > sort_factor2:           return +1 
    elif abs(symbol_diff1) < abs(symbol_diff2): return -1
    elif abs(symbol_diff1) > abs(symbol_diff2): return +1
    elif symbol_diff1 > symbol_diff2:           return -1
    elif symbol_diff1 < symbol_diff2:           return +1
    else:                                       return 0        
pass    



# --------------------------------------------------------------------------------------------------
def SortByWordGroups (given_word_pronun_list):


    # ------------------------------------------------------------------------------------
    def CountLetterOccurances():
        
        letter_counts = {}
        
        for charseq, pronunciation, count in given_word_pronun_list:
            for ch in charseq:
                letter_counts[ch] = letter_counts.get(ch,0) + 1
        return letter_counts


    # ------------------------------------------------------------------------------------
    # Comment:  The word and pronuncation are already lists of symbols.                   
    #           Convert to strings temporarily to remove duplicates.                      
        
    def SortUniquePronunciations (letter_counts_tbl):
        
        word_pronun_table_uniq = {}
        
        # Step 1. Find uniq (word, pronun) pairs index by 'word_group' keys. 
        #         Word group keys are (num_letters, symbol_count_diff) pairs.

        for charseq, pronunciation, count in given_word_pronun_list:  
            num_letters = len (charseq)
            num_phones  = len (pronunciation)  
            symbol_diff = num_letters - num_phones
                
            key = (num_letters, symbol_diff)
            val = (tuple(charseq), tuple(pronunciation))
             
            if word_pronun_table_uniq.has_key (key):
                word_pronun_table_uniq[key][val] = True
            else:
                word_pronun_table_uniq[key] = {val:True}
                             

        # Step 2. Sort the words in each word group according to character count.
            
        sorted_word_pronun_table = {}
            
        key_list = word_pronun_table_uniq.keys()
        key_list.sort()    
            
        for key in key_list:
            pronunciation_list = word_pronun_table_uniq[key].keys()
            pronunciation_list.sort()
            sorted_word_pronun_table [key] = pronunciation_list
                
                
        """
        # this is really slow
        for key in key_list:
            sorted_word_pronun_table[key] = []
            pronunciation_list = word_pronun_table_uniq[key].keys()
                
            print 'Sorting word group list', key, len(pronunciation_list)
                 
            charset_used  = set()
            sortable_list = []
                
            for word, pronun in pronunciation_list:
                #print word
                word_chars = set()
                word_letter_count = 0
                for ch in word:
                    if ch not in word_chars:
                        word_letter_count += letter_counts_tbl.get(ch,0)
                        word_chars.add(ch)    
                    #print ch, word_letter_count, word_chars
                #if len(word) == 2: print word, word_letter_count        
                #sys.exit()                
                sortable_list.append ([word_letter_count, word, pronun])        
        

            while sortable_list:            
                sortable_list.sort (reverse=False)
                best_item = sortable_list.pop()
                    
                for ch in best_item[1]: charset_used.add(ch)
                #print charset_used

                #for item in sortable_list: print item

                #a1 = list (string.split (best_item[1]))
                #a2 = list (string.split (best_item[2]))
                a1 = list (best_item[1])
                a2 = list (best_item[2])        
                new_item = (a1, a2)
                    
                
                #if len(best_item[1]) == 2: print best_item, '***'
                
                sorted_word_pronun_table[key].append (new_item)

                for i, (old_count, word, pronun) in enumerate (sortable_list):
                    word_chars = set()
                    word_letter_count = 0
                    for ch in word:
                        if ch not in charset_used and ch not in word_chars:
                            word_letter_count += letter_counts_tbl.get(ch,0)
                            word_chars.add(ch)        
                    sortable_list[i][0] = word_letter_count
        """

        return sorted_word_pronun_table
    pass
        

    letter_counts_histogram  = CountLetterOccurances()
    sorted_word_pronun_table = SortUniquePronunciations (letter_counts_histogram)
    sorted_wordgroup_keys    = sorted_word_pronun_table.keys()
    sorted_wordgroup_keys.sort (cmp = ComparePairKeys)
        
        
    return sorted_wordgroup_keys, sorted_word_pronun_table
pass
    


# --------------------------------------------------------------------------------------------------
def WriteWordListGrouped (given_key_list, pronunciation_table, outfile_pathname):
    
   #outfile = file (outfile_pathname, 'w')
    outfile = codecs.open (outfile_pathname, 'w', 'utf-8')
    word_count = 0

    for key in given_key_list:
        N = len (pronunciation_table [key])                         # number of words in group
        
        outfile.write ('\n%s with %i words in group\n' %(key, N))
            
        word_list = pronunciation_table [key]
            
        for charseq, pronun_seq in word_list:
            word_count += 1
            word   = string.join (charseq,'')
            pronun = string.join (pronun_seq,' ')
            outfile.write ('%6i. %s -> /%s/ \n' %(word_count, word, pronun))

    outfile.close()
pass        



# --------------------------------------------------------------------------------------------------
def WriteWordListHistogram (given_key_list, pronunciation_table, output_pathname):

    if output_pathname == '':
        outfile = sys.stdout
    else:
       #outfile = file (output_pathname, 'w')        
        outfile = codecs.open (output_pathname, 'w', 'utf-8')



    outfile.write ('Sorted word list divided into %i groups\n' %(len(given_key_list)) )
    outfile.write ('  starting with %s and ending with %s\n\n' %(given_key_list[0], given_key_list[-1]))
        
    num_words_by_length  = {}
    diff_count_by_length = {}

    for key in given_key_list:
        l = key[0]                                                  # length of word group, in chars
        d = key[1]                                                  # num letters - num phones      
        n = len (pronunciation_table [key])                         # number of words in group      
        num_words_by_length[l]  = num_words_by_length.get(l,0) + n
        diff_count_by_length[l] = diff_count_by_length.get(l,[]) + [d]
            
    total_words  = 0    
    word_lengths = num_words_by_length.keys()
    word_lengths.sort()
        
    outfile.write (' Histogram of word lengths\n\n')    
    outfile.write ('%4s %6s %6s  %s\n' %('Len', 'Num', 'Cumm', 'LenDiff'))

    for l in word_lengths:
        n = num_words_by_length[l]
        total_words += n
        outfile.write ('%4i %6i %6i  %s\n' %(l, n, total_words, str(diff_count_by_length[l])))
    outfile.write ('\n')
        

    if outfile != sys.stdout: outfile.close()
pass



    
# ----------------------------------------------------------------------------------------------
def WriteProductionsToSchemeFile (output_pathname, production_counts,  phone_name_convert={}): 
    
    outfile = codecs.open (output_pathname, 'w', 'utf-8')

    outfile.write ('%s\n\n' %( "(require 'lts_build)"))    
    outfile.write ('%s\n' %( '(set! allowables'))
    outfile.write ('%7s (%s ' %('','(#'))
    outfile.write (' %s)\n' %('#'))    
        

    lts_productions = {}
    sorted_production_list = [(val,key) for (key, val) in production_counts.items()]
    sorted_production_list.sort()
    sorted_production_list.reverse()
        
    for cnt, (usage_count, production) in enumerate (sorted_production_list):
        lhs = string.join (production[0],'')
        rhs = string.join (production[1],'-')
        lts_productions [lhs] = lts_productions.get(lhs,[]) + [rhs]
    

    # -------------------------------
    lhs_keys = lts_productions.keys()
    lhs_keys.sort (cmp = LatinCharacterSet.OrderLetters)
        
    for i, lhs in enumerate (lhs_keys):
        rhs_productions = lts_productions[lhs]
        rhs_productions.sort()    
        outfile.write ('%8s (%s ' %('',lhs))    

        for rhs in rhs_productions:
            if not rhs: rhs = '_'
            # need the next two lines because the phone names may be disguised
            rhs_string = map ((lambda x: phone_name_convert.get(x,x)), rhs.split('-'))
            rhs_string = string.join (rhs_string,'-')    
            outfile.write (' %s' %(rhs_string))
        outfile.write(')\n')
    outfile.write('))\n')
        
    outfile.close()
pass        



