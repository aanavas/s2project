# FestivalInterface.py
# ====================
# 0.01.001  22-Dec-2005  jmk  Split off from FestivalInterface.
# --------------------
    
import os
import string

# Note: This is just a stop-gap
# Really it needs to be configured through a function call.
#   lhs = common ascii form
#   rhs = globalphone form 
        
Global_Phones_Table = \
    {'A'  : 'M_a',
     'AE' : 'M_ae',
     'AL' : 'M_al',
     'E'  : 'M_e',
     'EI' : 'M_ei',
     'EL' : 'M_el',
     'EU' : 'M_eu',
     'I'  : 'M_i',
     'IL' : 'M_il',
     'O'  : 'M_o',
     'OE' : 'M_oe',
     'OL' : 'M_ol',
     'U'  : 'M_u',
     'UE' : 'M_ue',
     'UL' : 'M_ul',
          
     'B'  : 'M_b',
     'C'  : 'M_c',   
     'CH' : 'M_tS',
     'D'  : 'M_d',
     'DH' : 'M_D',   
     'DZ' : 'M_dZ',
     'F'  : 'M_f',
     'G'  : 'M_g',
     'H'  : 'M_h',
     'HH' : 'M_h',
     'J'  : 'M_dZ',
     'K'  : 'M_k',
     'KH' : 'M_kh',
     'L'  : 'M_l',
     'LL' : 'M_L',
     'M'  : 'M_m',
     'N'  : 'M_n',
     'NG' : 'M_ng',
     'NJ' : 'M_nj',
     'NQ' : 'M_nq',
     'PH' : 'M_ph',   
     'P'  : 'M_p',
     'R'  : 'M_r9',
     'RF' : 'M_rfd',    
     'RR' : 'M_r',
     'S'  : 'M_s',
     'SH' : 'M_S',   
     'SR' : 'M_sr',
     'T'  : 'M_t',
     'Th' : 'M_th',
     'TH' : 'M_T',
     'TS' : 'M_ts',
     'V'  : 'M_v',
     'W ' : 'M_w',
     'X ' : 'M_x',
     'Y ' : 'M_j',
     'Z ' : 'M_z',
     'ZH' : 'M_Z',
          
    }

            

# Check for some necessary environment variables, but still
# keep going if they don't exist.                          
    
#if not os.environ.has_key ('FESTDIR'):
#    print 'WARNGING: no environment variable set for FESTDIR (Festival directory)'
        
#if not os.environ.has_key ('IPA_SYNTHESIZER_DIR'):
#    print 'WARNGING: no environment variable set for IPA_SYNTHESIZER_DIR'
        

# 1. working directory of IPA voice             
# 2. path of festival binary (assumed in path)  
# 3. where the synthesized wavefiles are written
# 4. the scheme script that Festival executes   
# 5. the template for the above                 
        
Synthesizer_Directory = os.environ.get ('IPA_SYNTHESIZER_DIR','')   
Synthesizer_Program   = os.path.join (os.environ.get ('FESTDIR',''), 'bin/festival')
Synth_Waves_Directory = 'synth_output'                          # with respect to Synthesizer_Directory 
Synth_Logfile_Output  = 'synth_log_file.scm'                    # located in Synthesizer_Directory      
Synth_Scheme_Template = '(begin (utt.save.wave (utt.synth (Utterance Text "$1")) "$2") (quit))'
    
