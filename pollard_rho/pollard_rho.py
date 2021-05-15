from sympy.core.numbers import igcd
    

def pollard_rho(N, f = lambda x, M: (pow(x, 2, M) + 7) % M):
    """Implements Brent's Modified Algorithm of Pollard's rho method
       as described by Algorithm 8.5.2 in Cohen's book
    """
    
    def backtrack(y):
        g = 1
        while g == 1:
            y = f(y, N)
            g = igcd(x1 - y, N)
        return g

    if N < 5:
        raise ValueError('pollard_rho should receive N > 4')
        
    # Initialize
    y, x, x1 = 2, 2, 2
    k, l, P  = 1, 1, 1
    c = 0
    # Accumulate product
    while k > 0:
        x = f(x, N)
        P = (P * (x1 - x)) % N
        c = c + 1
        if c == 20:
            g = igcd(P, N)
            if g > 1:
                return backtrack(y)
            else:
                y,c = x, 0
        # Advance
        k = k - 1
        if k == 0:
            g = igcd(P, N)
            if g > 1:
                return backtrack(y)
            else:
                x1, k, l = x, l, 2 * l
                for i in range(k):
                    x = f(x, N)
                y, c = x, 0
    return N
