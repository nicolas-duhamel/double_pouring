We present a semi-algorithm for the double pouring problem, it may fail to terminate but whenever it terminates it does so in O(log n) steps.

It remains to prove that there exists an appropriate choice of initialization that turns the semi-algorithm into a genuine algorithm, i.e., guarantees termination on all instances.

Here is an example of experimental test:

n bits          | Lattice         | Frei            | Winner
---------------------------------------------------------------------------
101             | 337             | 1889            | Lattice
101             | 314             | 2317            | Lattice
101             | 300             | 2075            | Lattice
101             | 315             | 2433            | Lattice
101             | 325             | 2168            | Lattice
101             | 277             | 1923            | Lattice
102             | 313             | 2044            | Lattice
100             | 311             | 1905            | Lattice
101             | 325             | 2129            | Lattice
101             | 293             | 2034            | Lattice
---------------------------------------------------------------------------
Summary: Lattice Wins: 10, Frei Wins: 0
