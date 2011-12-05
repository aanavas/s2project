# Logger.py                                                                 
# =========                                                                 
# 0.01.007  21-Sep-2007  jmk  Added datestamp to logging prefix string.     
# 0.01.005  11-May-2004  jmk  Ignore with_linefeed when writing to file.    
# 0.01.004  03-Jun-2003  jmk  Automatic indendation based on level.         
# 0.01.003  23-Apr-2003  jmk  Added GetFuctionName.                         
# 0.01.002  23-Apr-2003  jmk  Incorporated logging to disk file.            
# 0.01.001  29-Jan-2003  jmk  Created.                                      
# --------------------------                                                
# Purpose: Simple filter around the print command.                          
#          Uses priority levels to control verbosity of printed messages.   
# --------------------------                                                

import string    
import traceback
import time

# Verbosity level conventions                                  
# Higher verbosity threshold results in fewer messages printing

Debug_Level    = 0
Detail_Level   = 1                  
Info_Level     = 2
Summary_Level  = 3
Major_Level    = 4
Warning_Level  = 5
Error_Level    = 6




# --------------------------------------------------------------------------------------------------
def GetFunctionName (module_name, length = 2):
    stack_list = traceback.extract_stack (limit = length+1)
    func_list  = map ((lambda x: x[2]), stack_list[:length])
    func_name  = string.join (func_list, '.')           
    return string.join ([module_name, func_name], '.')
pass




# --------------------------------------------------------------------------------------------------
class T:

    # --------------------------------------------------------------------------
    def __init__ (self, default_stdout_level = Info_Level, 
                        default_file_level   = Detail_Level,
                        default_prefix       = '--'):
        
        self.SetVerbosityLevel (default_stdout_level, default_file_level)
        self.prefix_string = default_prefix
        self.outfile = None    
                

    # --------------------------------------------------------------------------
    def SetVerbosityLevel (self, stdout_level=-1, outfile_level=-1):
        if stdout_level != -1:  self.stdout_verbosity_level  = stdout_level
        if outfile_level != -1: self.outfile_verbosity_level = outfile_level
            

    # --------------------------------------------------------------------------
    def GetVerbosityLevel (self):
        return (self.stdout_verbosity_level, self.outfile_verbosity_level)


    # --------------------------------------------------------------------------
    def OpenOutputFile (self, pathname):
        self.outfile = open (pathname, 'w')

         
    # --------------------------------------------------------------------------
    def CloseOutputFile (self):
        self.outfile.close()

            
    # --------------------------------------------------------------------------
    def write (self, message, level = Info_Level, with_linefeed = True):

        datestamp = string.replace (time.asctime (time.localtime(time.time())), ' ', '_')
        prefix = '%s %s %s' %(self.prefix_string, datestamp, '  ' * max (0, Warning_Level - level))
        
        if level >= self.stdout_verbosity_level:
            if with_linefeed:
                print level, prefix, message
            else:
                print level, prefix, message,        

        if self.outfile != None and not self.outfile.closed:
            if level >= self.outfile_verbosity_level:
                self.outfile.write ('%i %s %s\n' %(level, prefix, message))
                """    
                if with_linefeed:
                    self.outfile.write ('%i %s %s\n' %(level, prefix, message))
                 else:        
                    self.outfile.write ('%i %s %s' %(level, prefix, message))
                """        
                self.outfile.flush()
            
