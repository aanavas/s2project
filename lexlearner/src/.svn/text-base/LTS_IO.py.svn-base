# LTS_IO.py                                                             
# =========                                                             
# 0.02.002  04-May-2007  jmk  Added ReadAllowablesFile.                 
# 0.02.001  14-Mar-2007  jmk  Revised to support utf-8.                 
# 0.01.001  07-Nov-2005  jmk  Collected printing and writing routines.  
# ---------------------                                                 

import codecs
import math    
import os, sys
import string    
import LatinCharacterSet
import ConfigPath
import TinyStats

from Column import column         

Epsilon_Char = '_'

utf = codecs.getencoder ('utf-8')


# --------------------------------------------------------------------------------------------------
def PrintableStringRHS (rhs_symbol_seq):
    answer = string.join (rhs_symbol_seq, '-')
    if answer == '': answer = Epsilon_Char
    return answer



# --------------------------------------------------------------------------------------------------
def ConvertPhoneSeqToString (phoneseq, phone_name_converter):

    ConvNames = (lambda x: phone_name_converter.get(x,x))
    new_phone_list = []
        
    for j, compound_phones in enumerate (phoneseq):
        #if j > 3: continue
        if compound_phones:
            new_phones = string.join  (map (ConvNames, compound_phones), '-')   # convert and join
            new_phone_list.append (new_phones)                                  # add to new list 
        else:
            new_phone_list.append (Epsilon_Char)

    if new_phone_list:            
        phone_seq_string = string.join (new_phone_list)
    else:
        phone_seq_string = '_'
                    
    return phone_seq_string 
pass
    
         
# --------------------------------------------------------------------------------------------------
def WeightedAve (given_list):
    
    answer = 0.0
    total_count = sum (column (given_list))

    for item_info in given_list:
        item_count  = item_info[0]
        item_value  = item_info[1]
        item_weight = float(item_count) / float(total_count)
        answer += item_weight * item_value
    return answer            




# --------------------------------------------------------------------------------------------------
def WriteProductionsSummary (output_filename, production_counts, phone_name_converter = {}):
        

    # ------------------------------------------------------------------------------------------
    def PrintFullProdList (production_list):
        
        entropy = TinyStats.ComputeEntropyFromSymbolCounts (production_counts.items())

        outfile.write ('LTS Productions ordered by count (entropy %6.4f):\n' %(entropy)) 
            
        for cnt, (usage_count, production) in enumerate (production_list):
            lhs = production[0]
            rhs = ConvertPhoneSeqToString ([production[1]], phone_name_converter)
            """ JMK!
            try:    
                outfile.write ('%4i. %6i %6s -> %s\n' %(cnt+1, usage_count, lhs, rhs))
            except UnicodeEncodeError:
                lhs_utf = utf(lhs)[0]
                outfile.write ('%4i. %6i %6s -> %s\n' %(cnt+1, usage_count, lhs_utf, rhs))
            """      
        outfile.write('\n')
    pass


    # ------------------------------------------------------------------------------------------
    def PrintCondensedList (production_list):
        
        # create table that maps lhs -> all rhs productions, with counts

        lts_productions = {}
            
        for cnt, (usage_count, production) in enumerate (sorted_production_list):
            lhs = production[0]
            rhs = production[1]    
            lts_productions [lhs] = lts_productions.get(lhs,[]) + [(rhs, usage_count)]
                

        # write out the results alphabetically
            
        outfile.write ('LTS Productions organized by letter:\n')

        lhs_keys = lts_productions.keys()
        lhs_keys.sort (cmp = LatinCharacterSet.OrderLetters)


        # First pass.
        production_info = []

        for i, lhs in enumerate (lhs_keys):
            rhs_productions = lts_productions[lhs]
            rhs_prod_counts = column (rhs_productions,1)
            rhs_prod_list   = column (rhs_productions,0)    
            rhs_display_str = ConvertPhoneSeqToString (rhs_prod_list, phone_name_converter)
            num_productions = sum (rhs_prod_counts)
            entropy = TinyStats.ComputeEntropyFromSymbolCounts (rhs_productions)
            perplexity = math.pow (2.0, entropy)   
            production_info.append ((num_productions, perplexity, len(rhs_display_str)) )

        try:
            max_rhs_string_length = max (column (production_info,2))
        except:        
            max_rhs_string_length = 1
             
        formatting_string = string.replace ('%4i. %6i %6.3f %4s -> %-Xs', 'X', str(max_rhs_string_length+2))


        # Second pass.
        for i, lhs in enumerate (lhs_keys):
            rhs_productions = lts_productions[lhs]
            rhs_prod_counts = column (rhs_productions,1)
            rhs_prod_list   = column (rhs_productions,0)    
            rhs_display_str = ConvertPhoneSeqToString (rhs_prod_list, phone_name_converter)
                
            num_productions, perplexity = production_info[i][:2]
            outfile.write ('%4i' %(i+1))    
            
            try:
                outfile.write (formatting_string %(i+1, num_productions, perplexity, lhs, rhs_display_str))
            except UnicodeEncodeError:
                lhs_utf = utf(lhs)[0]
                outfile.write (formatting_string %(i+1, num_productions, perplexity, lhs_utf, rhs_display_str))
            
            for j, prod_count in enumerate (rhs_prod_counts):
                #if j > 3: continue
                outfile.write ('%6i' %(prod_count))
            outfile.write('\n')
        outfile.write('\n')
            

        perplexity_list = column (production_info,1)
            
        if perplexity_list:
            min_perplexity = min (perplexity_list)
            max_perplexity = max (perplexity_list)
        else:        
            min_perplexity = 0
            max_perplexity = 0

        outfile.write ('Num letter productions: %5i\n'  %(len(sorted_production_list)))    
        outfile.write ('Min letter perplexity: %6.3f\n' %(min_perplexity))
        outfile.write ('Max letter perplexity: %6.3f\n' %(max_perplexity))
        outfile.write ('Ave letter perplexity: %6.3f\n' %(WeightedAve(production_info)))
        outfile.write ('\n')
            
        return lts_productions
    pass
                

    # case 1. open a file suitable for writing utf-8 strings
    # case 2. most likely this is sys.stdout                
        
    if type (output_filename) == type('string'):
        outfile = codecs.open (output_filename, 'w', 'utf-8')    
    else:
        outfile = output_filename
    
    
    phone_names_list = phone_name_converter.items()
    phone_names_list.sort()
    """    
    outfile.write ('Disguised Phone Names:\n')
    for hidden_name, real_name in phone_names_list:
        outfile.write ('%4s -> %s\n' %(hidden_name, real_name))
    outfile.write ('\n')
    """        
    sorted_production_list = [(val,key) for (key, val) in production_counts.items()]
    sorted_production_list.sort (reverse=True)
                
    PrintFullProdList (sorted_production_list)
    ans = PrintCondensedList (sorted_production_list)
                                                         
    if type (output_filename) == type('string'):
        outfile.close()
        
    return ans
pass




# --------------------------------------------------------------------------------------------------
def WriteOutProductions (outfile_pathname, productions_list):
    
    outfile = codecs.open (outfile_pathname, 'w', 'utf-8')
            
    outfile .write ('%6s  %-15s %6s   %-24s %6s   %3s %3s    %-12s\n'  
        %('Word#', 'Align#', 'Word', 'Pronun', 'Prod#', 'Ltr', 'Num', 'Phone'))
    
    for prod_num, item in enumerate (productions_list):
        word_num, align_num, char_seq, phone_seq, prod_lhs, prod_rhs = item
        
        word_string   = string.join (char_seq,'')
        phone_seq_str = string.join (phone_seq)    
        #rhs_prods_str = string.join (map ((lambda x: string.join(x,'-')), allowable_prod_lhs[prod_lhs]))

        outfile.write ('%6i. %i %20s = %-24s |  %3i.  %3s (%i) -> %-12s\n' \
            %(word_num,
                align_num,   
                word_string, 
                phone_seq_str,    
                prod_num + 1,
                string.join (prod_lhs,''),
                0,                                #len (allowable_prod_lhs [prod_lhs]),
                string.join (prod_rhs,'-'),
                ))
        
    outfile.close()
pass



# --------------------------------------------------------------------------------------------------
def WriteOutSolutions (solutions_filename, given_solutions):
    

    # --------------------------------------------------------------------------------------------------
    def WriteOutLetterToSoundSolutions (outfile, word_counter, charseq, phoneseq, solutions, include_failures=False):
        
        word = string.join (charseq,  '')
        pron = string.join (phoneseq, ' ')    
        
        if solutions: 
            for cnt, (score, soln) in enumerate (solutions):
                total_score = reduce ((lambda x,y: x+y), column(soln,2)) 

                outfile.write ('  %5i.  Soln %i %5.0f  %20s : %-40s |' \
                    %(word_counter, cnt+1, total_score, word, pron))
                                    
                for (source, target, score) in soln:
                    num_chars = 1 + int (math.log (max(1.0,score),10.0))
                    spacer = ' ' * max (0, (5 - num_chars))
                    if len(target) == 0: target = ('_')
                        
                    outfile.write (' %2s [%i] %s -> %-6s' \
                        %(string.join(source,''), 
                          score, spacer, 
                          string.join(target) ))
                
                outfile.write('\n')
                    
                    
        elif include_failures:
            outfile.write ('  %5i.  FAILED  %5s %20s : %-40s |' %(word_counter, '', word, pron))
            outfile.write (' %2s -> %-5s\n' %(word, ''))
        pass
            

    word_solutions_outfile = codecs.open (solutions_filename, 'w', 'utf-8')
        
    word_solutions_outfile.write ('  %5s   Soln %1s %5s  %20s   %-40s %s\n' 
        %('Word#', '#', 'Score', 'Word', 'Pronuncation', 'Production Sequence'))


    for loop_cnt, item in enumerate (given_solutions):
        charseq   = item[0]
        phoneseq  = item[1]    
        solutions = item[2]
        WriteOutLetterToSoundSolutions (word_solutions_outfile, loop_cnt+1, charseq, phoneseq, solutions, include_failures=True)
            
    word_solutions_outfile.close()
pass        



# --------------------------------------------------------------------------------------------------
def WriteOutRules (output_filename, lts_rule_system, phone_name_converter = {}, include_sorted_rule_list = False):
    
    # --------------------------------------------------------------------------
    # Added this to protect from automatic conversion to unicode through xml-rpc
    # This is just a short term fix before fully supporting UTF-8.              
        
    def Enc (given_string, encoding = 'latin-1'):
        if type (given_string) == type ('ascii'):
            return given_string
        else:
            return given_string.encode (encoding)



    # case 1. open a file suitable for writing utf-8 strings
    # case 2. most likely this is sys.stdout                
        
    if type (output_filename) == type('string'):
        outfile = codecs.open (output_filename, 'w', 'utf-8')    
    else:
        outfile = output_filename
        

    rule_count = 0
    lhs_symbol_list = lts_rule_system.keys()
    lhs_symbol_list.sort (cmp = LatinCharacterSet.OrderLetters)
    lhs_perplexity_list = []    
    

    # find the right width for the rhs part
    M = max_rhs_symbol_length = 0
        
    sorted_rule_list = []
        

    for lhs in lhs_symbol_list:
        lts_rule_chain = lts_rule_system[lhs]
        for rule_context, rhs_symbol_seq, application_count in lts_rule_chain:
            rhs_string  = string.join (rhs_symbol_seq,'-')
                
           #M = max (M, len(Enc(rhs_string)))
            M = max (M, len(utf(rhs_string)))
                 
            sorted_rule_list.append ((application_count, lhs, rhs_symbol_seq, rule_context))
                
    format_str = string.replace ('%6i. %2s -> %Xs / %s [%i] %s', 'X', str(M))


    outfile.write ('LTS Rule System:\n')
    outfile.write ('%6s  %6s\n' %('Count','Perplexity'))    

    for lhs in lhs_symbol_list:
        lts_rule_chain = lts_rule_system[lhs]
            
        entropy = TinyStats.ComputeEntropyFromSymbolCounts (column (lts_rule_chain,1,3))
        perplexity = math.pow (2.0, entropy)
        application_total = sum (column (lts_rule_chain,2))    
        lhs_perplexity_list.append ((application_total, perplexity))
         
        outfile.write ('%6i %6.3f' %(len(lts_rule_chain), perplexity))

        for rule_context, rhs_symbol_seq, application_count in lts_rule_chain:
            rhs_symbol_seq = map ((lambda x: phone_name_converter.get(x,x)), rhs_symbol_seq)
            rule_count += 1    
            lhs_symbol  = rule_context[1]
            context_str = rule_context[0] + '_' + rule_context[2]
            rhs_string  = string.join (rhs_symbol_seq,'-')
            num_chars   = 1 + int (math.log (max(1.0,application_count),10.0))
            spacer      = ' ' * max (0, (10 - num_chars - len(context_str)))
            if rhs_string == '': rhs_string = '_'
                
            lhs_utf = utf(lhs_symbol)[0]
            rhs_utf = utf(rhs_string)[0]
            ctx_utf = utf(context_str)[0]       
                
                
           #outfile.write (format_str %(rule_count, Enc(lhs_symbol), Enc(rhs_string), Enc(context_str), application_count, spacer))
           #outfile.write (format_str %(rule_count, lhs_utf, rhs_utf, ctx_utf, application_count, spacer))
            outfile.write (format_str %(rule_count, lhs_symbol, rhs_string, context_str, application_count, spacer))
                  
        outfile.write('\n')


    perplexity_list = column (lhs_perplexity_list,1)
        
    if perplexity_list:
        min_perplexity = min (perplexity_list)
        max_perplexity = max (perplexity_list)
    else:        
        min_perplexity = 0
        max_perplexity = 0

    outfile.write ('\n')
    outfile.write ('Number of LTS rules: %i\n' %(rule_count))            
    outfile.write ('Min lts rule perplexity: %6.3f\n' %(min_perplexity))
    outfile.write ('Max lts rule perplexity: %6.3f\n' %(max_perplexity))
    outfile.write ('Ave lts rule perplexity: %6.3f\n' %(WeightedAve(lhs_perplexity_list)))
    outfile.write ('\n')
        

    if include_sorted_rule_list:
        sorted_rule_list.sort (reverse=True)
        outfile.write ('Rules sorted by count:')
            
        for i, (rule_count, lhs, rhs, rule_context) in enumerate (sorted_rule_list):
            rhs_symbol_seq = map ((lambda x: phone_name_converter.get(x,x)), rhs)
            context_str = rule_context[0] + '_' + rule_context[2]
            rhs_string  = string.join (rhs_symbol_seq,'-')
            outfile.write ('\n')
            outfile.write (format_str %(i+1, lhs, rhs_string, context_str, rule_count, ''))
        outfile.write ('\n\n')
pass



# --------------------------------------------------------------------------------------------------
def ReadAllowablesFile (input_pathname):
    
    word_pronun_list = []
    phonemes_encountered = set()
        
    # Read in the allowables file                                                       
    # Format: letter followed by one more phonemes, where the phoneme may be compound   
    # Compounds are joined by hyphens, and phones phones separated by spaces            
    #   ex. u UW OW                                                                     
    #   ex. x K K-X                                                                     
            
    if os.path.exists (input_pathname) and os.path.isfile (input_pathname):
        infile = codecs.open (input_pathname, 'r', 'utf-8')
        
        # There is one G2P relation per line e.g:   
        #   a AA                                    
        #   b B                                     
            
        for rawline in infile.readlines():
            line = rawline.strip()
            if not line or line[0] == '#': continue
            fields = line.split()
            
            # Note: the call to replace dash with space allows for multi-productions
            # to be defined as part of the default grapheme-to-phoneme relations.   
            # E.g. 'x' -> K-S -> /K S/                                              
                
            if len (fields) >= 2:
                letter = fields[0]
                phoneme_list = fields[1:]
                    
                for maybe_a_compound_phoneme in phoneme_list:
                    phoneme_mod = maybe_a_compound_phoneme.replace('-',' ')
                    phoneme_seq = tuple (phoneme_mod.split())
                    word_pronun_list.append ((letter, phoneme_seq, 1))
                        
                    for ph in phoneme_seq:
                        phonemes_encountered.add(str(ph))

    return word_pronun_list, phonemes_encountered
pass



# --------------------------------------------------------------------------------------------------
def ReadPhoneList (phoneset_file_pathname):
        
    phoneset = set()
        
    if os.path.exists (phoneset_file_pathname) and os.path.isfile (phoneset_file_pathname):
        infile = file (phoneset_file_pathname,'r')

        for rawline in infile.readlines():
            line = rawline.strip()
            if not line: continue
            fields  = line.split()
            if not fields: continue
            phoneset.add (fields[0])
        infile.close()

    return phoneset
pass

