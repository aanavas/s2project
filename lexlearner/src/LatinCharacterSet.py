# CharacaterSet.py
# ================
# 0.01.001  23-Oct-2005  jmk  Copied from find_lexicion_allowables.
# ---------------------
    


# --------------------------------------------------------------------------------------------------
def OrderLetters (str1, str2):

    def LetterOrd (char):
        if   ord(char) in range(224,230+1): return ord('a') + 0.1 * float(ord(char) - 223)
        elif ord(char) in range(231,231+1): return ord('c') + 0.1 * float(ord(char) - 231)
        elif ord(char) in range(232,235+1): return ord('e') + 0.1 * float(ord(char) - 231)
        elif ord(char) in range(236,239+1): return ord('i') + 0.1 * float(ord(char) - 235)
        elif ord(char) in range(241,241+1): return ord('n') + 0.1 * float(ord(char) - 240)
        elif ord(char) in range(242,246+1): return ord('o') + 0.1 * float(ord(char) - 241)
        elif ord(char) in range(249,251+1): return ord('u') + 0.1 * float(ord(char) - 248)
        elif ord(char) in range(253,255+1): return ord('u') + 0.1 * float(ord(char) - 252)
        else: return ord(char)

    N = min (len(str1), len(str2))
        
    for i in range(N):
        ord_ch1 = LetterOrd (str1[i]) 
        ord_ch2 = LetterOrd (str2[i]) 
        if   ord_ch1 < ord_ch2: return -1
        elif ord_ch1 > ord_ch2: return +1
            
    if   len(str1) < len(str2): return -1
    elif len(str1) > len(str2): return +1
    else: return 0            
pass        


