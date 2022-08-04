    

def calIndexSearch(s_m, s_d, a_m, a_d):
    index = 0
    if a_m - 1 == s_m:
        if s_m == 7 or 8 or 10 or 12 or 1:
            index = 31 - s_d + a_d
            return index
        else:
            index = 30 - s_d + a_d
            return index      
    elif a_m - 2 == s_m:
        if s_m == 7 or 8 or 10 or 12 or 1:
            if a_m - 1 == 7 or 8 or 10 or 12 or 1:    
                index = 31 - s_d + a_d + 31
                return index
            else:
                index = 31 - s_d + a_d + 30
                return index
        else:
            if a_m - 1 == 7 or 8 or 10 or 12 or 1:    
                index = 30 - s_d + a_d + 31
                return index
            else:
                index = 30 - s_d + a_d + 30
                return index            
    elif a_m == s_m:
        if s_m == 7 or 8 or 10 or 12 or 1:
            index = a_d - s_d
            return index
        else:
            index = a_d - s_d
            return index

                
