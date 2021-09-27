import math

import argparse

def calculate_chance(start_rate, full_rate, encounters):
    chance = get_probability(start_rate,full_rate,encounters)

    return_obj = {}
    if (start_rate >= 1 and full_rate >= 1 and encounters>= 1):
        return_obj['chance_not_get_per'] = chance["miss"]	 
        return_obj['chance_to_get_per'] = chance["get"]
        return_obj['next_chance_per'] = chance["next_chance"] 

        return_obj['start_rate'] = str(start_rate)
        return_obj['full_rate'] = str(full_rate)
        return_obj['encounters'] = str(encounters)

        return(return_obj)

def get_probability(base_chance, total_outcomes, num_encounters):
    p1 = base_chance
    p2 = total_outcomes
    p3 = num_encounters
    v1 = p2-p1
    v6 = v1/p2
    v3 = math.pow(v6, p3)
    v12 = (1-v3)*100
    v5 = v3*100
    if (v12 > 0.001 and v5 > 0.001):
        v12 = round(v12*100,2)/100
        v5 = round(v5*100,2)/100
    elif (v5 < 0.001):
        v12 = ">99.999"
        v5 = "<0.001"
    elif (v12 < 0.001):
        v12 = "<0.001"
        v5 = ">99.999"
    
    tot_chance = round((base_chance/total_outcomes)*10000,4)/100

    chance = {}
    chance["encounters"] = str(num_encounters)
    chance["miss"] = str(round(v5,2)) 
    chance["get"] = str(round(v12,2))
    chance["next_get"] = str(base_chance)+" in "+str(total_outcomes)
    chance["next_chance"] = str(round(tot_chance,2))
    return chance

if __name__=="__main__":
    # Initialize parser
    parser = argparse.ArgumentParser()

    # Set cli args
    parser.add_argument('-s', '--start_rate', default=1, help = 'Base chance in ratio')
    parser.add_argument('-f', '--full_rate', default=4096, help = 'Full chance in ratio')
    parser.add_argument('-n', '--num_encounters', default=1, help = 'Number of encounters so far')
    # Read arguments from command line
    args = parser.parse_args()

    calculate_chance(int(args.start_rate), int(args.full_rate), int(args.num_encounters))