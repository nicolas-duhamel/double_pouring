from functools import reduce
import random
import math

def gcd(lst):
    return reduce(math.gcd, lst)


def solve_lattice(a, b, c):
    curr_c = [-b, a, 0]
    curr_v = [a, b, c]
    steps = 0
    max_steps = 4000000
    
    while steps < max_steps:
        assert curr_v[0] * curr_c[0] + curr_v[1] * curr_c[1] + curr_v[2] * curr_c[2] == 0
        
        if any(v == 0 for v in curr_v):
            return steps
            
        candidates = []
        
        for i in range(3):
            for j in range(3):
                if i == j:
                    continue
                    
                if curr_v[j] < curr_v[i]:
                    continue
                    
                if curr_c[i] % 2 != curr_c[j] % 2:
                    continue
                    
                new_val = (curr_c[i] + curr_c[j]) // 2
                score = abs(curr_c[i] - new_val)
                if score == 0:
                    continue
                candidates.append((score, i, j, new_val))
                
        if not candidates:
            return -1
            
        candidates.sort(key=lambda x: x[0])
        best_score, src, tgt, new_c_val = candidates[0]
        
        curr_v[src] *= 2
        curr_v[tgt] -= curr_v[src] // 2
        curr_c[src] = new_c_val
        
        steps += 1
        
    return -1


def perform_move(vessels, src_idx, tgt_idx):
    amount = vessels[tgt_idx]
    if vessels[src_idx] < amount:
        return False
        
    vessels[tgt_idx] *= 2
    vessels[src_idx] -= amount
    return True


def janson_round(vessels):
    idx = sorted(range(3), key=lambda k: vessels[k])
    a_idx, b_idx, c_idx = idx[0], idx[1], idx[2]
    
    a = vessels[a_idx]
    b = vessels[b_idx]
    
    if a == 0:
        return []
        
    p = b // a
    if p == 0:
        return []
        
    num_bits = p.bit_length()
    moves = []
    
    for i in range(num_bits):
        bit = (p >> i) & 1
        
        if bit == 1:
            moves.append((b_idx, a_idx))
        else:
            moves.append((c_idx, a_idx))
            
    return moves


def frei_round(vessels):
    idx = sorted(range(3), key=lambda k: vessels[k])
    a_idx, b_idx, c_idx = idx[0], idx[1], idx[2]
    
    a = vessels[a_idx]
    b = vessels[b_idx]
    
    if a == 0:
        return []
        
    p = b // a
    q = (b + a - 1) // a
    
    r1 = b - (p * a)
    r2 = (q * a) - b
    
    moves = []
    
    if r1 <= r2:
        return janson_round(vessels)
    else:
        limit = q.bit_length() - 1
        
        for i in range(limit):
            bit = (q >> i) & 1
            if bit == 1:
                moves.append((b_idx, a_idx))
            else:
                moves.append((c_idx, a_idx))
                
        moves.append((a_idx, b_idx))
        
        return moves


def solve_with_frei(a, b, c):
    v = [a, b, c]
    total_moves = 0
    max_steps = 1000000
    
    while total_moves < max_steps:
        if any(x == 0 for x in v):
            return total_moves
            
        moves = frei_round(v)
        
        if not moves:
            break
            
        for src, tgt in moves:
            if not perform_move(v, src, tgt):
                return -1
            total_moves += 1
            
    return total_moves


def run_comparison():
    print(f"{'n bits':<15} | {'Lattice':<15} | {'Frei':<15} | {'Winner'}")
    print("-" * 75)
    
    wins_lattice = 0
    wins_frei = 0
    
    for _ in range(100):
        a = random.randint(1, 2**100)
        b = random.randint(1, 2**100)
        c = random.randint(1, 2**100)
        
        steps_lattice = solve_lattice(a, b, c)
        steps_frei = solve_with_frei(a, b, c)
        
        if steps_lattice < steps_frei and steps_lattice != -1:
            winner = "Lattice"
            wins_lattice += 1
        else:
            winner = "Frei"
            wins_frei += 1
            
        s_lat = str(steps_lattice) if steps_lattice != -1 else "FAIL"
        s_frei = str(steps_frei) if steps_frei != -1 else "FAIL"
        
        print(f"{(a+b+c).bit_length():<15} | {s_lat:<15} | {s_frei:<15} | {winner}")
        
    print("-" * 75)
    print(f"Summary: Lattice Wins: {wins_lattice}, Frei Wins: {wins_frei}")


run_comparison()
