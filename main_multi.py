import itertools
import random
from multiprocessing import Pool
import time

CHEMO_DAYS = [(2,3), (11, 18), (32, 39), (60, 67)]

# how much I don't like the things we are modeling
PICC_BASELINE_COST = 1 # annoyance of just having picc in
PICC_PLACEMENT_COST = 100

ER_NO_PICC_COST = 1000 # if go to ER without picc
INFECTION_COST = PICC_PLACEMENT_COST * 100 


INFECTION_CHANCE = 4 / 1000 # per 1000 catheter days
ER_CHANCE = 1.0 # 0-1 chance of going to ER 7 days after chemo  
ER_DAYS_AFTER = 6 # how many days after when roll for chemo

SIMS_TO_RUN = 100000

# input= A B C D
# A
# A B
# A C
# A D
# A B C 

def generate_all_picc(chemo_dates: list[tuple[int, int]]):
    solutions = []
    # want all possible places you COULD place/remove a picc
    # do this by taking all combinations up to how many chemo sessions there are
    for i in range(1, len(chemo_dates)+1):
        solutions.extend(list(itertools.combinations(chemo_dates, i)))
    
    # need to remove solutions that are 
    # A. 2 or more elements
    # B. contain the last chemo session 

    for j in solutions:
        print(j)
    return solutions

def test_infection():
    c = 0
    for i in range(100000):
        if random.random() < INFECTION_CHANCE:
            print("Got infection")
            c += 1
    print(f"Idealized infection chance {INFECTION_CHANCE} found chance {round(c/100000, 3)}")

# solution is a tuple with all the chemo sessions that the picc is taken out after 
def model_solution(chemo_dates: list[tuple[int, int]], solution: tuple[tuple[int, int]], debug=False, print_func=print):
    picc_in = True
    # infection is modeled as you roll the current chance, and is cumulative (adding INFECTION_CHANCE) per day
    infection_chance = INFECTION_CHANCE
    days_until_ER_roll = -999 # after chemo, set to 7 and decremented each day until it is time to see if we went to the ER
    total_cost = 0
    days_to_pull_picc = [x[1]+1 for x in solution]
    days_to_insert_picc = [x[0] for x in chemo_dates]
    times_infected = 0

    # each day until the end of chemo
    for day in range(1, chemo_dates[-1][1]+1):
        if days_until_ER_roll >= 1: days_until_ER_roll -= 1

        if days_until_ER_roll == 0:
            days_until_ER_roll = -999
            if random.random() < ER_CHANCE and not picc_in:
                #print("going ER WITHOUT PICC!")
                total_cost += ER_NO_PICC_COST
        
        # check if its a day we take out/place picc
        if day in days_to_pull_picc:
            picc_in = False
            days_until_ER_roll = ER_DAYS_AFTER

        if day in days_to_insert_picc and not picc_in:
            picc_in = True
            total_cost += PICC_PLACEMENT_COST
            #print("Placed picc")
        
        # roll infection
        if picc_in and random.random() < INFECTION_CHANCE:
            #print("Got infection")
            times_infected += 1
            total_cost += INFECTION_COST # @TODO could maybe also add the cost of a new line?
            infection_chance = INFECTION_CHANCE # reset
        
        # if not, add up the chance for next time
        else:
            infection_chance += INFECTION_CHANCE

        # if we have picc add baseline cost
        if picc_in: total_cost += PICC_BASELINE_COST        
        #print(f"day {day} cost {total_cost} picc {picc_in}")
    return total_cost, times_infected


def print_results(inp):
    for i in inp:
        sol, avg_cost, t_infections = i
        print(f"Solution: {sol}\nAvg Cost {avg_cost}\nTotal Infections {t_infections}\n")

def run_sim(inp_sol):
    total_cost = 0
    total_infections = 0
    for i in range(SIMS_TO_RUN):
        sol_cost, num_infections = model_solution(CHEMO_DAYS, inp_sol, debug=False)
        total_cost += round(sol_cost, 1)
        total_infections += num_infections
    #results.append((sol, total_cost/SIMS_TO_RUN, total_infections))
    #print(f"\nSolution {inp_sol}\n total avg cost {total_cost/SIMS_TO_RUN} total infections {total_infections}\n")
    return (inp_sol, total_cost/SIMS_TO_RUN, total_infections)


def find_optimal_solution(infection_cost, placement_cost, er_no_picc_cost, infection_chance_per_1000):
    global INFECTION_COST, PICC_PLACEMENT_COST, ER_NO_PICC_COST, INFECTION_CHANCE
    INFECTION_COST = infection_cost
    INFECTION_CHANCE = infection_chance_per_1000 / 1000
    PICC_PLACEMENT_COST = placement_cost
    ER_NO_PICC_COST = er_no_picc_cost
    solutions = generate_all_picc(CHEMO_DAYS)

    s = time.perf_counter()
    result = []

    pool = Pool()
    result = pool.map(run_sim, solutions)
    e = time.perf_counter() - s
    print(f"Total time {e}")
    return result


if __name__ == "__main__":
    results = find_optimal_solution()
    print(results)
    

    results.sort(key = lambda x: x[1]) # avg cost
    print("==========AVG COST RESULTS===========")
    print_results(results)

    results.sort(key = lambda x: x[2]) # total infections
    print("==========TOTAL INFECTION RESULTS===========")
    print_results(results)
