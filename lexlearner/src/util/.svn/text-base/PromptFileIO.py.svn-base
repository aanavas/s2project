# PromptFile_IO.py
# ================
# 0.01.001  14-Jun-2005  jmk  Finally put label reading routines in a common place.
# ---------------------

import codecs
import string
    


# --------------------------------------------------------------------------------------------------
# Function: ReadOneFile()                                                                           
# Purpose:  Loads utterances from a prompt file                                                     
# Example:                                                                                          
#   ( vowels_01 "beet" )                                                                            
#   ( vowels_02 "bit"  )                                                                            
#   ( vowels_03 "bait" )                                                                            

def ReadOneFile (pathname):

    answer = {}
    #infile = file (pathname, 'r')
    infile = codecs.open (pathname, 'r', 'utf-8')
 
    for i in range(2500):
        line = infile.readline()
        print line[:16]    

    for rawline in infile.readlines():
        line = rawline.strip()
        if not line or line[0] == '#': continue
            
        line = line[1:-1].strip()
        line = string.replace (line, '"', '')
            
        fields = string.split (line, maxsplit=1)
        if len(fields) < 2: continue
        
        prompt_name, prompt_string = fields
        answer [prompt_name] = prompt_string
        print prompt_name    
    infile.close()
        
    return answer
pass
    

# --------------------------------------------------------------------------------------------------
# Function: WriteOneFile()                                                                          
# Purpose:  Loads utterances from a prompt file                                                     
    
def WriteOneFile (pathname, prompt_list):
    
    #outfile = file (pathname,'w')
    outfile = codecs.open (pathname, 'w', 'utf-8')
         
    for prompt_name, prompt_text in prompt_list:
        outfile.write ('( %s "%s" )\n' %(prompt_name, prompt_text))
    outfile.close()
pass
    
            

Read  = ReadOneFile
Write = WriteOneFile
    
