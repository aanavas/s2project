# scan_for_lexlearners.py                   
# =======================                   
# 0.01.001  04-Apr-2007  jmk  Created.      
# ------------------------------------      

import getopt
import os, sys, string
import socket    
import xmlrpclib
        


# --------------------------------------------------------------------------------------------------
def ScanPorts (low_port_num, high_port_num, verbose):
    """
    Purpose:
        Scan IP port ranges for the presence of lexlearner servers.
    
    Params:
        low_port_num   scan from this port number
        high_port_num  to this port number
        verbose        if true, report status for every port
                       if false, only for ports where a lexlearner was found
    Bugs:
        It will get stuck on ports begin listened to by non-python services, 
        such as ftp and http.
    
    Example Output:
        port  8000: no server found
        port  8001: no server found
        port  8002: unknown server found
        port  8003: no server found
        port  8004: no server found
        port  8005: no server found
        port  8006: no server found
        port  8007: no server found
        port  8008: lexlearner found with id ../dicts/festdict-0.7a.4k_sample
        port  8009: no server found
        port  8010: no server found
    """

    for port_number in range (low_port_num, high_port_num+1):
        server  = xmlrpclib.Server ('http://localhost:%s' %(port_number))
        message = ''

        try:
            response = server.GetServerIdentification()
            message  = 'lexlearner found with id %s' %(response)
        except socket.error, msg:
            if verbose: message = 'no server found'
        except xmlrpclib.Fault, msg:
            if verbose: message = 'unknown server found'

        if message:
            print 'port %5i: %s' %(port_number, message)



# ==============
# Mainline code.
# ==============

Default_Low_Port_Num  = 8000
Default_High_Port_Num = 9000

if __name__ == '__main__':
    possible_flags = ['help', 'low=', 'high=', 'verbose']
        
    try:
        opt_list, prog_args = getopt.getopt (sys.argv[1:], 'h', possible_flags)
    except getopt.GetoptError, msg:
        sys.exit ('\nGetopt Error: %s\n' %(msg))
        
    option_table = dict (opt_list)


    if '-h' in option_table or '--help' in option_table:
        print 
        print 'Format: %s FLAGS' %(sys.argv[0])
        print '%10s [%i]  %s' %('--low=',    Default_Low_Port_Num,  'scan from this port number')
        print '%10s [%i]  %s' %('--high=',   Default_High_Port_Num, 'to this port number')
        print '%10s [%s]  %s' %('--verbose', 'False', 'if present print status of every port')
        print


    try:
        low_port_num  = int (option_table.get ('--low',  Default_Low_Port_Num))
        high_port_num = int (option_table.get ('--high', Default_High_Port_Num))
        verbosity     = '--verbose' in option_table
    except ValueError, msg:
        print 'Error: %s\n' %(msg)
        sys.exit()


    ScanPorts (low_port_num, high_port_num, verbosity)

