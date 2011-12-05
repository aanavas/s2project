# FestivalInterface.py                                                              
# ====================                                                              
# 0.01.004  03-Nov-2008  jmk  Added diagnostic output file of ConfigurePhoneNames.  
# 0.01.003  24-Feb-2006  jmk  Write the wavefile beneath the current directory.     
# 0.01.002  05-Jan-2006  jmk  Added ConfigurePhoneNames.                            
# 0.01.001  02-Nov-2005  jmk  Cheap interface to Featival IPA-phone synthesizer.    
# --------------------                                                              
    
import os
import shutil    
import string
import ConfigPath    
import FestivalConfig as FC

# Note: SCF = 'Synthesizer Control File'
from FestivalConfig import Synth_Scheme_Template as SCF_template    

   

# -------------------------------------------------------------------------------------------------
# Purpose: Synthesize a sequence of phones (using the Festival IPA synthesizer.)                   
# Returns: The pathname of the synthesized wavefile.                                               
# Output:  The wavefile (if things go well), and the scheme code that is executed (in a log file). 
        
global call_count
call_count = 0
    
def SynthesizePhoneSeq (phone_seq, id_string='', verbose=False):

    global call_count
    call_count += 1

    # set various pathnames                
    # if needed create the output directory
        
    global_phones_seq = map ((lambda ph: FC.Global_Phones_Table.get(ph,'')), phone_seq)
    global_phones_str = string.join (global_phones_seq)
    output_wavename   = 'synth_%s_%s.wav' %(id_string, string.zfill (call_count, 4))
    output_wavedir    = os.path.join (os.path.abspath('.'), FC.Synth_Waves_Directory)
    output_wavepath   = os.path.join (output_wavedir, output_wavename)
    output_wavepath2  = os.path.join (output_wavedir, 'synth.wav')
         
    if not os.path.exists (output_wavedir): os.makedirs (output_wavedir, mode=0777)
       
    # Fill in the scheme code that Festival will execute.
    scheme_script = string.replace (SCF_template,  '$1', global_phones_str)
    scheme_script = string.replace (scheme_script, '$2', output_wavepath)
        
    # Construct and execute the command.
    # Note that festival has to be running in the voice's top diretory.
    command_string = "%s festvox/cmu_ipa_phones_clunits.scm '%s'" %(FC.Synthesizer_Program, scheme_script)
        
    # Write this out to the logfile.
    outfile = file (FC.Synth_Logfile_Output, 'a')
    outfile.write  (command_string + '\n')
    outfile.close()

    current_dir = os.getcwd()
    os.chdir  (FC.Synthesizer_Directory)
    os.system (command_string)    
    os.chdir  (current_dir)

    if os.path.exists (output_wavepath):
        shutil.copyfile (output_wavepath, output_wavepath2)

    # some debugging printout
    if verbose:
        print command_string
        print call_count, phone_seq, global_phones_str

    return output_wavepath
pass
    



# -------------------------------------------------------------------------------------------------
def ConfigurePhoneNames (pathname, outpath='phone_mapfile.txt'):
    
    if os.path.exists (pathname) and os.path.isfile (pathname):
        infile = file (pathname, 'r')
        FC.Global_Phones_Table = {}
    
        for rawline in infile.readlines():
            line = rawline.strip()
            if not line: continue
            fields = string.split (line)
                
            if len(fields) >= 2:
                users_phone_name = fields[0].strip()
                globalphone_name = fields[1].strip()
                FC.Global_Phones_Table [users_phone_name] = globalphone_name
        infile.close()
    
    if outpath: 
        namelist = sorted(FC.Global_Phones_Table.items())
        outfile = file (outpath,'w')
        for user_name, global_phone_name in namelist:
            outfile.write ('%4s %s\n' %(user_name, global_phone_name))
        outfile.close()        
                     
    return True        
pass



# ---------------
#  Mainline code.
# ---------------
    
if __name__ == '__main__':
    SynthesizePhoneSeq (['B', 'I', 'M'], id_string='test_1', verbose=True)


