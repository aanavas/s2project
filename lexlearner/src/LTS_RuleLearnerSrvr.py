# LTS_RuleLearnerSrvr.py                                                        
# ======================                                                        
# 0.02.006  07-May-2007  jmk  Added a version check before calling SimpleXMLRPC.
# 0.02.005  21-Apr-2007  jmk  Search a range of ports for a connection.         
# 0.02.004  21-Apr-2007  jmk  Now employ a ReusableSimpleXMLRPCServer.          
# 0.02.003  05-Mar-2007  jmk  Added launch notification file writing.           
# 0.02.002  18-Mar-2007  jmk  Use codec.open in PrimeWithAllowables.            
# 0.02.001  14-Mar-2007  jmk  Revised to support utf-8.                         
# 0.01.001  08-Nov-2005  jmk  Created.                                          
# ---------------------                                                         

import codecs
import getopt
import string
import os, sys    
import time
import socket    

import DictionaryIO
import FestivalInterface
import Logger
import LTS_IO
import LTS_RuleLearner
import PromptFileIO

from datetime import datetime
from StringIO import StringIO
from Column   import column
from SimpleXMLRPCServer import SimpleXMLRPCServer



# --------------------------------------------------------------------------------------------------
# Purpose:  An IP port will often be keep tied up by the OS for a few minutes even after it has been
#           dropped by an application. The result is that re-running lexlearner on a port number it 
#           used previously will fail (can't connect) even though you'd think it should be avilable.
#           Setting allow_reuse_address to True get's around this limitation.                       
# Docs:     http://www.dalkescientific.com/writings/diary/archive/2005/04/21/  (found by Matt)      
#           Search for the keyword SO_REUSEADDR to find the relevant discussion                     
    
class ReusableSimpleXMLRPCServer (SimpleXMLRPCServer):
    allow_reuse_address = True

     

# --------------------------------------------------------------------------------------------------
# Methods:
#   Shutdown            
#   GetNextWord
#   GetNextWordRemove
#   GetWorkingDirectory
#   GetServerIdentification
#   SetServerIdentification
#   Get_LTS_Rules
#   RemoveFromLexicon
#   SubmitPronunciation
#   GetRecentWordPronuns
#   PredictOneWord        
#   SynthesizePhoneSeq
#   SynthesizeWord
#   ConfigurePhoneNames
  
        
class T (LTS_RuleLearner.T):
    """
        No docs yet.
    """        
    
       
    # ---------------------------------------------------------------------------------------------
    # Purpose:  Shut down the server gracefully.                                                   
    # Params:   None                                                                               
    # Comment:  sys.exit() doesn't do the job, so calls os._exit() instead.                        
    #                                                                                              
    def Shutdown (self):
        self.textlog.write (Logger.GetFunctionName(__name__))
        print 'Shutdown request received'
            
        current_time = datetime.now()
        outfile = file (Launch_Notice_Filename,'a')
        outfile.write ('Shutting down: %s\n' %(current_time.ctime()))
        outfile.close()
            
        high_number = 0

        for filename in os.listdir('.'):
            if os.path.isfile (filename) and filename.find (Launch_Notice_Filename) > -1:
                name_fields = filename.split('.')
                try:
                    high_number = max (high_number, int(name_fields[-1]))
                except ValueError:
                    pass        

        saved_filename = '%s.%i' %(Launch_Notice_Filename, high_number+1)
        os.system ('mv %s %s' %(Launch_Notice_Filename, saved_filename))    
        os._exit(0)


    # ---------------------------------------------------------------------------------------------
    def GetWorkingDirectory (self):
        self.textlog.write (Logger.GetFunctionName(__name__))
        return os.getcwd()
     
  
    # ---------------------------------------------------------------------------------------------
    def GetServerIdentification (self):
        self.textlog.write (Logger.GetFunctionName(__name__))
        if not 'server_id_string' in dir(self):
            self.server_id_string = 'LTS_RuleLeanerSrvr'    
        return self.server_id_string
            
     
    # ---------------------------------------------------------------------------------------------
    def SetServerIdentification (self, given_id_string):
        self.textlog.write (Logger.GetFunctionName(__name__))
        self.server_id_string = given_id_string
        return True
 

    # ----------------------------------------------------------------------------------------------
    # Returns: The next word as a string or the emptry string if there are no more words.           
    # Comment: Depending on the particular word selector it might return a character sequence rather
    #          than a string, but we always want to return a string to the web client application.  
    # Comment from Yunghui, Nov 30 2005:                                                            
    #       I've read the document about how PHP handles exception.                                 
    #       If I have to implement a "try - catch" pair to catch the exception from your            
    #       LTS_server, it will add on the complexity of the PHP codes since there'll be            
    #       two level of error handling (one for exception, one for xml rpc function                
    #       error condition), which makes life harder. So can we just make an agreement             
    #       that let your GetNextWord function return a null string when there's no more            
    #       words? That will make debug and maintainance of the code easier. Thanks.                
    # Warning: printing unicode to stdout only works if the locale supports 
    #   unicode, as opposed to ascii. e.g. locale gives LANG=en_US.UTF-8    
    #   Also, if lexlearner server is launched with stdout redirected to a  
    #   file (as it is in spice), the output device suddenly is ascii.      
    #   This breaks with a exceptions.UnicodeEncodeError.ascii.             
        
    def GetNextWord (self):
        self.textlog.write (Logger.GetFunctionName(__name__))
        try:
            word_charseq = super(T,self).GetNextWord()
            word_string  = string.join (word_charseq,'')
            #print 'GetNextWord', word_charseq, word_string
        except IndexError:
            word_string = ''
        return word_string

            
    # ---------------------------------------------------------------------------------------------
    def GetNextWordRemove (self):
        self.textlog.write (Logger.GetFunctionName(__name__))
        word_charseq = super(T,self).GetNextWord()
        word_string  = string.join (word_charseq,'')
        self.HappyWithWord (word_charseq)
        return word_string


    # ---------------------------------------------------------------------------------------------
    def Get_LTS_Rules (self):
        self.textlog.write (Logger.GetFunctionName(__name__))
        writer = StringIO()
        LTS_IO.WriteOutRules (writer, self.GetRules(), self.phone_name_inverse_table) 
        return writer.getvalue()    


    # ---------------------------------------------------------------------------------------------
    def RemoveFromLexicon (self, given_word):
        self.textlog.write (Logger.GetFunctionName(__name__))
        return super(T,self).RemoveFromLexicon (tuple(given_word))
    
            
    # ---------------------------------------------------------------------------------------------
    def SubmitPronunciation (self, given_word, given_pronun, stype='batch'):
        self.textlog.write (Logger.GetFunctionName(__name__))
            
        word_char_seq = (tuple (given_word))
        pronunciation = string.split (given_pronun)
        disguised_pronunciation = pronunciation   
        disguised_pronunciation = map ((lambda x: self.phone_name_disguise_table.get(x,x)), pronunciation)
        
        log_file = codecs.open ('pronunciation.log', 'a', 'utf-8')
        log_file.write ('("%s" nil (%s))\n' %(given_word, string.join(pronunciation)))    
        log_file.close()    

        super(T,self).SubmitPronunciation (word_char_seq, disguised_pronunciation, stype)
        return len (self.word_pronun_list)
            


    # ---------------------------------------------------------------------------------------------
    def GetRecentWordPronuns (self, max_words_to_get):
        self.textlog.write (Logger.GetFunctionName(__name__))
        
        N = len (self.word_pronun_list)
        M = max_words_to_get
        writer = StringIO()
        
        for i in range (N-1, max(-1,N-M-1), -1):
            charseq, phoneseq, word_count = self.word_pronun_list[i]
            writer.write ('%s "%s"\n' %(string.join(charseq,''), string.join(phoneseq)))
            
        return writer.getvalue()



    # ---------------------------------------------------------------------------------------------
    def PredictOneWord (self, given_word, max_pronuns_to_predict):
        self.textlog.write (Logger.GetFunctionName(__name__))
        
        word_char_seq = tuple (given_word)
            
        if max_pronuns_to_predict < 1:
            return ''
        elif max_pronuns_to_predict == 1:
            predicted_pronun, alignment = super(T,self).PredictOneWordPronun (word_char_seq)
            predicted_pronun_str = string.join (predicted_pronun)
            return predicted_pronun_str
        else:        
            predicted_pronun_list = super(T,self).PredictMultipleWordPronuns (word_char_seq)
            return predicted_pronun_list [:max_pronuns_to_predict]



    # ---------------------------------------------------------------------------------------------
    def SynthesizePhoneSeq (self, phone_seq, id_string):
        self.textlog.write (Logger.GetFunctionName(__name__))
        
        if type (phone_seq) == type('string'):
            phone_seq = tuple (string.split (phone_seq))
            
        return FestivalInterface.SynthesizePhoneSeq (phone_seq, id_string)



    # ---------------------------------------------------------------------------------------------
    def SynthesizeWord (self, given_word, id_string):
        self.textlog.write (Logger.GetFunctionName(__name__))
        phone_seq = string.split (self.PredictOneWord (given_word, 1))
        return self.SynthesizePhoneSeq (phone_seq, id_string)
    

    # ---------------------------------------------------------------------------------------------
    def ConfigurePhoneNames (self, pathname):
        self.textlog.write (Logger.GetFunctionName(__name__))
        return FestivalInterface.ConfigurePhoneNames (pathname)

     
# end class T.
# ============



# --------------------------------------------------------------------------------------------------
def IsFile(filename): return os.path.exists(filename) and os.path.isfile (filename)


# --------------------------------------------------------------------------------------------------
def WriteNotificationFile (file_pathname, options_table, lexlearner_obj, ip_port_number, launch_time):
    current_time = datetime.now()
        
    outfile = file (file_pathname,'w')
    outfile.write ('%s\n' %(sys.argv[0]))
    for key, val in sorted (options_table.items()):
        outfile.write ('%20s  %s\n' %(key, val))

    outfile.write ('LexLearner ID: %s\n' %(lexlearner_obj.GetServerIdentification()))
    outfile.write (' Listening on: %i\n' %(ip_port_number))
    outfile.write (' Time to load: %3.2f s\n' %(launch_time))    
    outfile.write (' Current time: %s\n' %(current_time.ctime()))    
    outfile.close()


# --------------------------------------------------------------------------------------------------
def AppendNotificationFile (file_pathname):
    current_time = datetime.now()
    outfile = file (Launch_Notice_Filename,'a')
    outfile.write ('Terminating LexLearner on: %s\n' %(current_time.ctime()))
    outfile.close()    



# --------------------------------------------------------------------------------------------------
Default_Port_Number = 8000
Highest_Port_Number = 16000
Port_Number_Range   = Highest_Port_Number - Default_Port_Number 
Launch_Notice_Filename = 'lexlearner_launch_info.txt'    

 
def LaunchServer():    
    # Delete the launch notification file if it happens to be hanging around
    # from a previous run (it shouldn't but could if the server was killed.)
        
    if os.path.exists (Launch_Notice_Filename):
        os.remove (Launch_Notice_Filename)


    # Define flag list and get command line option.     
    # Note: either --festdict or --lexlist is required  

    flag_list = [('help',        'this command'),
                 ('port=',       'IP port number for communication with xml server (default 8000)'),
                 ('workdir=',    'specifies the working directory to use (defaults to current)'),
                 ('phoneset=',   'filename of list of phonemes'),
                 ('prompts=',    'filename of festival-format prompt list'),   
                 ('festdict=',   'filename of festival-format pronunciation dictionary'),
                 ('lexlist=',    'filename of word list with word frequency counts'),
                 ('ignore=',     'filename of festival-format list of words to ignore (eg. those lexlearned previously)'),
                 ('allowables=', 'filename of (partial) list of LTS allowables (optional)'),
                 ('newpronuns=', 'filename of existing list of word pronunciations (optional)'),
                 ('rules=',      'filename of a pickled rule set that has previously been learned')]

    try:
        opt_list, prog_args = getopt.getopt (sys.argv[1:], '', column(flag_list))
        option_tbl = dict (opt_list)
    except getopt.GetoptError, msg:
        print 'Error', msg
        sys.exit('      type --help for program options\n')


    # Print out the options if requested.

    if option_tbl.has_key('--help'):
        print 'python', sys.argv[0]
        for option_flag, description in flag_list:
            print '%12s %s' %(option_flag, description)
        print
        sys.exit()    


    # Step 0. Print out option table.
        
    print sys.argv[0]
    for key, val in sorted (option_tbl.items()):
        print '%20s  %s' %(key, val)
    print        


    # Step 1. Change to the working directory. Try to create if it doesn't exist.
    #         If this is parameter is not specified use the current directory.   
        
    t1 = time.time()
    working_dir = '.'
        
    if option_tbl.has_key ('--workdir'):
        working_dir = option_tbl['--workdir']
        try:
            if not os.path.exists (working_dir):
                print 'Creating new working directory:', working_dir
                os.makedirs (working_dir)
            os.chdir (working_dir)
            print 'Changing to working directory:', working_dir
        except OSError, msg:
            print msg
            sys.exit()    
                

    # Step 2. If provided, read in G2P associations - called the "allowable productions".
       
    allowables_phoneset = set()
    allowable_productions = []    
    allowables_file_pathname = option_tbl.get('--allowables','')

    if IsFile (allowables_file_pathname):
        print '\nReading allowables file %s' %(allowables_file_pathname)
        allowable_productions, allowables_phoneset = LTS_IO.ReadAllowablesFile (allowables_file_pathname)
        print '  num grapheme productions: %i' %(len(allowable_productions))
        print '  done in %3.2f s' %(time.time()-t1)
    else:
        print 'Warning: %s does not exist' %(allowables_file_pathname)
        

    # Step 3. Ignore the contained words.   
        
    words_to_ignore = set()
    ignore_file_pathname = option_tbl.get('--ignore','')
        
    if IsFile (ignore_file_pathname):
        print '\nReading', ignore_file_pathname
        infile = codecs.open (ignore_file_pathname, 'r', 'utf-8')
        for rawline in infile:
            word = unicode (rawline.strip())
            if word: words_to_ignore.add (word)
        infile.close()
        print '  num words to ignore: %i' %(len(words_to_ignore))                

       
    # Step 4. Read in words that we have pronunciations for (from previous runs). 
    #         These words are ignored when asking the user for new pronunciations.
        
    provided_word_pronuns = []

    if '--newpronuns' in option_tbl:
        pronunciation_file = option_tbl['--newpronuns']
        
        if IsFile (pronunciation_file):
            print '\nReading ', pronunciation_file
            provided_word_pronuns = DictionaryIO.ReadFestivalDictionary (pronunciation_file, words_only=False)
            print '  num words with pronunciations: %i' %(len(provided_word_pronuns))


    # Step 5. Read in the festival dictionary, if provided.                     
    # The Festival dictionary has word pronunciations but not frequency counts. 
        
    t2 = time.time()    
    fest_word_list = []    
    festdict_file_pathname = option_tbl.get('--festdict','')
            
    if IsFile (festdict_file_pathname):
        print '\nReading festival dictionary file', festdict_file_pathname
        fest_word_list = DictionaryIO.ReadFestivalDictionary (festdict_file_pathname, words_as_charseq=False)
        print '  read %i words in %3.3f s' %(len(fest_word_list), time.time()-t2)
            
            
    # Step 6. Read in the lexicon file. This contains words we want pronunciations  
    # for. The LexList format has occurance counts for each word.                   
        
    t3 = time.time()
    corpus_word_list = []
    lexicon_file_pathname = option_tbl.get('--lexlist','')
            
    if IsFile (lexicon_file_pathname):
        print '\nReading word freq file', lexicon_file_pathname
        corpus_word_list = DictionaryIO.ReadLexiconFileWithCounts (lexicon_file_pathname, sorted_by_count=True)
        print '  read %i words in %3.3f s' %(len(corpus_word_list), time.time()-t3)


    # Step 7. Remove words that are in the ignore list.
        
    if words_to_ignore:
        print '\nIgnoring %i entries from %s' %(len(words_to_ignore), option_tbl['--ignore']) 

        temp_wordlist = []
        for item in corpus_word_list:
            word = item[0]
            if word not in words_to_ignore:
                temp_wordlist.append (item)
        corpus_word_list = temp_wordlist
        print '  num words remaining: %i' %(len(corpus_word_list))
            

    # Step 8a. Add pronunciations from the supplied festival dictionary.    
    #          Note: I'm not certain which list should overwrite the other. 
        
    if fest_word_list:
        print '\nAdding pronunciations from', festdict_file_pathname

        t2 = time.time()
        fest_word_tbl = {}
        for item in fest_word_list:
            word = item[0]
            fest_word_tbl[word] = item   
        found_count = 0

        for i, item in enumerate(corpus_word_list):
            word = item[0]
            if word in fest_word_tbl:
                pronun = fest_word_tbl[word][1]
                corpus_word_list[i][1] = pronun
                found_count += 1
        print '  num pronunciations found in %3.3f s: %i' %(time.time()-t2, found_count)
            
        found_count = 0
        for word, pronun, count in corpus_word_list:
            if pronun: found_count += 1
        print '  have %i of %i word pronunciations' %(found_count, len(corpus_word_list))
    
                    
    # Step 8b. Add pronunciations from previous runs of lexlearner.
        
    if provided_word_pronuns:
        print '\nAdding pronunciations from', pronunciation_file

        t2 = time.time()
        provided_word_tbl = {}
        for item in provided_word_pronuns:
            word = item[0]
            provided_word_tbl[word] = item   
        found_count = 0
                   
        for i, item in enumerate(corpus_word_list):
            word = item[0]
            if word in provided_word_tbl:
                pronun = provided_word_tbl[word][1]
                corpus_word_list[i][1] = pronun
                found_count += 1
                print i,pronun    
        print '  num pronunciations found in %3.3f s: %i' %(time.time()-t2, found_count)
    
    
    # Step 8c. Count number of pronunciations we have for the word list.
        
    print '\nCounting pronunciations'
    found_count = 0
    corpus_pronun_tbl = {}    
        
    for word, pronun, count in corpus_word_list:
        if pronun: 
            found_count += 1
            corpus_pronun_tbl[word] = pronun    
    print '  have %i of %i word pronunciations' %(found_count, len(corpus_word_list))


    # step 9.  Read transcript of recorded prompts and extract words.   
    #          If there are any uncovered words in the prompts list     
    #          then those are what goes into prompt_list, instead of    
    #          the lexicon words.                                       
        
    prompt_word_list = []
    prompt_file_pathname = option_tbl.get('--prompts','')
            
    if IsFile (prompt_file_pathname):
        print '\nReading prompts %s' %(prompt_file_pathname)

        recorded_prompt_tbl  = PromptFileIO.Read (prompt_file_pathname)
        all_words_in_prompts = {} #set()

        for prompt_name, prompt in recorded_prompt_tbl.items():
            prompt_words = prompt.split()
            for raw_word in prompt_words:
                word = DictionaryIO.TrimExternalPunctuation (raw_word)
                #if word not in words_to_ignore:    
                #    all_words_in_prompts.add(word) 
                all_words_in_prompts[word] = all_words_in_prompts.get(word,0) + 1
            
        temp_word_list = []
        for word, count in all_words_in_prompts.items():
            temp_word_list.append ([count,word])
        temp_word_list.sort (reverse=True)
            
        prompt_word_list = [[w,'',c] for c,w in temp_word_list]
        found_count = 0
                
        for i, item in enumerate(prompt_word_list):
            word = item[0]
            if word in corpus_pronun_tbl:
                found_count += 1
                prompt_word_list[i][1] = corpus_pronun_tbl[word]
        print '  have %i of %i word pronunciations in prompt word list' %(found_count, len(prompt_word_list))


   # Step 10. Create the LTS Learner object
   #lts_learner = T (prompt_word_list, unknown_phone_symbol='*') 
    lts_learner = T (prompt_word_list, corpus_word_list, unknown_phone_symbol='*') 


    # Step 11. Disguise the phoneme names. This basically allows any utf-8 strings   
    # to be used as phone names, since the algorithm will manipulate '01' '02' etc. 

    explicit_phoneset = set()
    phoneset_file_pathname = option_tbl.get('--phoneset','')   
    
    if IsFile (phoneset_file_pathname):
        print '\nReading phoneset file', phoneset_file_pathname
        explicit_phoneset = LTS_IO.ReadPhoneList (phoneset_file_pathname)
        print '  num phonemes: %i' %(len(explicit_phoneset))    
            

    # Step 12. Initialialize with LTS rules or G2P assosciations, if provided.

    have_word_pronuns = []
    have_word_pronuns.extend (allowable_productions)
    have_word_pronuns.extend (fest_word_list)
    have_word_pronuns.extend (provided_word_pronuns)
        
    print '\nLearning Rules from all provided word pronunciations'
    print '  num saved pronunciations: %i' %(len(have_word_pronuns))
        
    t2 = time.time()
    lts_learner.DisguisePhonemeNames (explicit_phoneset | allowables_phoneset)
    lts_learner.PrimeWithPronunciations (have_word_pronuns)
    t3 = time.time()
            
    print '  num rules learned: %i' %(lts_learner.GetNumberOfRules())    
    print '  done in %3.3f s' %(t3-t2)
        

    # Step 13. Write out rules to scm file.
        
    scm_lexrules_pathname = os.path.join (working_dir, 'lexrules.scm')
    print '\nWriting out rules in Festival format to %s' %(scm_lexrules_pathname)
        
    lts_learner.WriteOutFestivalRules (scm_lexrules_pathname)
    lts_learner.WriteOutLexicon ('Janus',    os.path.join(working_dir,'dictionary'))
    lts_learner.WriteOutLexicon ('Festival', os.path.join(working_dir,'dictionary-festival'))


    # Step 14. Read in pickled rule file.
    #          Note:  not sure if this is still works with the php scripts.
    """    
    if '--rules' in option_tbl:
        rule_file_pathname = option_tbl['--rules']
        if os.path.exists (rule_file_pathname) and os.path.isfile (rule_file_pathname):
            lts_learner.LoadStateInfoRules (rule_file_pathname)
            print '\nReading LTS rules from %s in %3.2f s' %(rule_file_pathname, time.time()-t1)
        else:
            print 'Warning: %s does not exist' %(rule_file_pathname)
    """
     
    print '\nSize of final word list: %i' %(len(corpus_word_list))
        

    # Step 15. Try to create a lexlerner object and connect it to an open IP port to    
    # receive xml-rpc commands. Run through the full range of permitted port numbers    
    # (hard-coded in this application) until an open port is found. The search starts   
    # at the number specified through the --port flag and gives up when the full range  
    # has been tested, rather than looping infinitely.                                  

    try:
        start_port_number = int (option_tbl.get ('--port',Default_Port_Number))
        num_ports_tried = 0

        while num_ports_tried < Port_Number_Range:
            asked_for_port_number = Default_Port_Number + \
                ((start_port_number + num_ports_tried) - Default_Port_Number) % Port_Number_Range

            try:
                # Step 15a. Create an xml_server object and register it.                            
                # The first call raises socket.error if the asked_for_port_number is not available. 

                version_value = float(sys.version_info[0]) + 0.1 * float(sys.version_info[1])

                if version_value >= 2.5:
                    xml_server = ReusableSimpleXMLRPCServer (('localhost', asked_for_port_number), encoding='utf-8')
                else:    
                    xml_server = ReusableSimpleXMLRPCServer (('localhost', asked_for_port_number))
                        
                xml_server.register_instance (lts_learner)
                    
                # Step 15b. If we get here things are good. Set the default server identification string.

                got_port_number = asked_for_port_number
                lts_learner.SetServerIdentification ('%i | %s' %(got_port_number, lexicon_file_pathname))
                t2 = time.time()

                # Step 15c. Write out a notification file.                                          
                # This file provides some basic information about the server and is deleted when    
                # the server is shut down. It can be used as an indication that the server is up    
                # (even though there is a brief moment where it isn't, so this is not strict).      

                WriteNotificationFile (Launch_Notice_Filename, option_tbl, lts_learner, got_port_number, t2-t1)
                    
                print 'Time to get ready: %3.3f s' %(t2-t1)
                print 'LTS LexLearner server coming up on port %i' %(got_port_number)
                
                # Step 15d. Now enter an infinite listen-reply loop and we are in business. 

                xml_server.serve_forever()
                return    
                    
            except socket.error, msg:
                num_ports_tried += 1
                print 'Error %s port %i' %(msg, asked_for_port_number)
                print 'Trying another port, attempt count %i\n' %(num_ports_tried+1)

    except ValueError:
        t2 = time.time()
        WriteNotificationFile (Launch_Notice_Filename, option_tbl, lts_learner, 0, t2-t1)
        
            
pass
    


# --------------
# Mainline code.
# --------------
    
if __name__ == '__main__':
    try:
        try:
            LaunchServer()
        finally:
            AppendNotificationFile (Launch_Notice_Filename)

    except socket.error, msg:
        print 'Fatal Error: %s\n' %(msg)
            
    except KeyboardInterrupt, msg:
        print 'Fatal Error: %s\n' %('keyboard interrupt')

