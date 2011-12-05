# Column.py                                                                     
# =========                                                                     
# 0.01.001  29-Jun-2005  jmk  Finally moved to its own file.                    
# ------------------------------------------------------------------------------
    

# ------------------------------------------------------------------------------
def column (given_list, col=0, end=0): 
    if end <= col:
        return map ((lambda x: x[col]), given_list)
    else:
        return map ((lambda x: x[col:end]), given_list)


