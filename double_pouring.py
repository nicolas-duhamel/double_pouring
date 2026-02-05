from functools import reduce
import random
import math

# ==========================================
# ALGORITHM 1: LATTICE BFS (The "Correct" Approach)
# ==========================================


# --- PART 1: FIND INITIAL COEFFICIENTS (KERNEL) ---
def get_initial_coeffs(a, b, c):
    """
    Finds a short integer vector (x,y,z) such that ax+by+cz=0.
    Uses LLL-style reduction on the kernel basis.
    """
    # 1. Start with Identity augmented with values
    rows = [[1, 0, 0, a], [0, 1, 0, b], [0, 0, 1, c]]

    # 2. Euclidean Reduction (Your Algorithm) to find Kernel Basis
    # We run until we have 2 rows with value 0 (Rank is 2)
    basis = []
    while len(basis) < 2:
        # Sort by magnitude of the dot product (column 3)
        rows.sort(key=lambda r: abs(r[3]))

        # If smallest is 0, we found a kernel vector! Move it to basis.
        if rows[0][3] == 0:
            basis.append(rows.pop(0))
            continue

        # Euclidean Step on the active rows
        # Subtract multiple of smallest from others
        smallest = rows[0]
        changed = False
        for i in range(1, len(rows)):
            factor = rows[i][3] // smallest[3]
            if factor != 0:
                for k in range(4):
                    rows[i][k] -= factor * smallest[k]
                changed = True

        # If nothing changed, we might be stuck (shouldn't happen with integers)
        if not changed and len(rows) > 0:
            raise ValueError("Unexpected: No reduction possible but rank not achieved.")

    # 3. Lagrange/Gaussian Reduction on the 2D Kernel Basis
    # (This ensures we get the "mixed" shortest vector)
    u = basis[0][:3]
    v = basis[1][:3]

    def norm_sq(vec):
        return sum(x * x for x in vec)

    while True:
        if norm_sq(v) < norm_sq(u):
            u, v = v, u  # Ensure u is shortest

        # Try to reduce v against u
        # Project v onto u: factor = round( (v.u) / (u.u) )
        dot = sum(u[i] * v[i] for i in range(3))
        mag = norm_sq(u)
        if mag == 0 or dot < mag:
            break  # v is as short as possible relative to u
        factor = dot // mag
        if dot % mag > mag // 2:
            factor += 1  # Round to nearest

        # v = v - factor * u
        v = tuple(v[i] - factor * u[i] for i in range(3))

    assert a * u[0] + b * u[1] + c * u[2] == 0
    assert a * v[0] + b * v[1] + c * v[2] == 0

    # Return the shorter of the two optimized basis vectors
    return u if norm_sq(u) <= norm_sq(v) else v


def gcd(lst):
    return reduce(math.gcd, lst)


# --- THE LATTICE SOLVER ---
def solve_lattice(a, b, c):
    """
    Solves by always picking the single 'best' valid move
    (steepest descent on coefficients) rather than searching a tree.
    """
    # shortest vector gets stuck
    # curr_c = list(get_initial_coeffs(a, b, c))
    curr_c = [-b, a, 0]
    curr_v = [a, b, c]
    steps = 0
    max_steps = 4000000  # Safety limit to prevent infinite loops

    # print(f"Start Invariant: {curr_c[0]}*A + {curr_c[1]}*B + {curr_c[2]}*C = 0")

    while steps < max_steps:
        assert (
            curr_v[0] * curr_c[0] + curr_v[1] * curr_c[1] + curr_v[2] * curr_c[2] == 0
        )

        # 1. Goal Check
        if any(v == 0 for v in curr_v):
            # print(f"SOLVED in {steps} steps! Final Vessels: {curr_v} Coeffs: {curr_c}")
            return steps

        # 2. Find ALL Valid Moves
        candidates = []

        for i in range(3):
            for j in range(3):
                if i == j:
                    continue

                # A. Physical Check: Target >= Source
                if curr_v[j] < curr_v[i]:
                    continue

                # B. Math Check: Parity must match
                if curr_c[i] % 2 != curr_c[j] % 2:
                    continue

                # C. Calculate Potential Result
                # This move is valid! Let's score it.
                new_val = (curr_c[i] + curr_c[j]) // 2

                # HEURISTIC: Minimize the magnitude of the changed coefficient.
                # This drives the algorithm towards 0.
                score = abs(curr_c[i] - new_val)
                if score == 0:
                    continue
                candidates.append((score, i, j, new_val))

        # 3. Greedy Selection
        if not candidates:
            print(f"Stuck at step {steps}. No valid moves available (Local Minimum).")
            # State: Vessels {curr_v}, Coeffs {curr_c}
            return -1

        # Sort by score (lowest absolute value of new coefficient is best)
        candidates.sort(key=lambda x: x[0])

        # Pick the winner
        best_score, src, tgt, new_c_val = candidates[0]

        # 4. Execute Move
        # Update Vessels
        curr_v[src] *= 2
        curr_v[tgt] -= curr_v[src] // 2

        # Update Coeffs
        curr_c[src] = new_c_val

        steps += 1

    print(curr_c)
    print(curr_v)
    print("Failed: Max steps reached.")
    return -1


# --- HELPER: BASIC MOVE ---
def perform_move(vessels, src_idx, tgt_idx):
    """
    Simulates pouring from src_idx -> tgt_idx.
    Constraint: vessels[tgt_idx] (recipient) doubles.
    vessels[src_idx] (giver) loses amount.
    """
    # Note: The prompt says "Pour from B to A".
    # Standard problem rule: Recipient doubles. Source reduces.
    # So "Pour B->A" means A doubles, B reduces.

    amount = vessels[tgt_idx]  # The amount A currently has
    if vessels[src_idx] < amount:
        return False  # Physical violation

    vessels[tgt_idx] *= 2
    vessels[src_idx] -= amount
    return True


# --- ALGORITHM 1: JANSON'S ROUND ---
def janson_round(vessels):
    # Input: a <= b <= c.
    # We work on a copy to track moves
    # Identify indices of sorted order
    # Indices: 0=Smallest(A), 1=Medium(B), 2=Largest(C)
    idx = sorted(range(3), key=lambda k: vessels[k])
    a_idx, b_idx, c_idx = idx[0], idx[1], idx[2]

    a = vessels[a_idx]
    b = vessels[b_idx]

    if a == 0:
        return []

    p = b // a
    if p == 0:
        return []

    # Bit decomposition of p
    # The loop goes 0..floor(log p)
    # This implies we iterate bits from LSB to MSB or just up to length.
    # Janson usually iterates to build up A.
    num_bits = p.bit_length()

    moves = []

    for i in range(num_bits):
        # Check ith bit of p
        bit = (p >> i) & 1

        if bit == 1:
            # "Pour from B to A" -> A doubles, B reduces
            # Recipient: A (a_idx), Source: B (b_idx)
            moves.append((b_idx, a_idx))
        else:
            # "Pour from C to A" -> A doubles, C reduces
            moves.append((c_idx, a_idx))

    return moves


# --- ALGORITHM 2: FREI'S ROUND ---
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

        # Final step: "Pour from A to B"
        # Liquid A -> B. B doubles, A reduces.
        # Recipient: B, Source: A
        moves.append((a_idx, b_idx))

        return moves


# --- SOLVERS ---


def solve_with_frei(a, b, c):
    v = [a, b, c]
    total_moves = 0
    max_steps = 1000000

    while total_moves < max_steps:
        if any(x == 0 for x in v):
            return total_moves

        # Determine round moves
        moves = frei_round(v)

        if not moves:
            break

        # Execute moves
        for src, tgt in moves:
            if not perform_move(v, src, tgt):
                return -1
            total_moves += 1

    return total_moves


# ==========================================
# COMPARISON HARNESS
# ==========================================


def run_comparison():
    print(
        f"{'n bits':<15} | {'Lattice (BFS)':<15} | {'Frei (Greedy)':<15} | {'Winner'}"
    )
    print("-" * 75)

    wins_lattice = 0
    wins_frei = 0

    # Generate random instances
    for _ in range(1000):
        a = random.randint(1, 2**100)
        b = random.randint(1, 2**100)
        c = random.randint(1, 2**100)

        steps_lattice = solve_lattice(a, b, c)
        steps_frei = solve_with_frei(a, b, c)

        # Determine winner
        if steps_lattice < steps_frei and steps_lattice != -1:
            winner = "Lattice"
            wins_lattice += 1
        else:
            winner = "Frei"
            wins_frei += 1

        # Formatting for infinite/failed runs
        s_lat = str(steps_lattice) if steps_lattice != -1 else "FAIL"
        s_frei = str(steps_frei) if steps_frei != -1 else "FAIL"

        print(f"{(a+b+c).bit_length():<15} | {s_lat:<15} | {s_frei:<15} | {winner}")

    print("-" * 75)
    print(f"Summary: Lattice Wins: {wins_lattice}, Frei Wins: {wins_frei}")


# Run it
run_comparison()
