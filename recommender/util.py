from scipy.sparse import lil_matrix
import subprocess
#from numpy import nonzero

def compute_intersection(a, b):
    """ Naive quadratic private set intersection.

    Returns: secret Array with intersection (padded to len(a)), and
    secret Array of bits indicating whether Alice's input matches or not 
    author:  (C) 2016 University of Bristol."""
    n = len(a)
    if n != len(b):
        raise CompilerError('Inconsistent lengths to compute_intersection')
    intersection = Array(n, sint)
    is_match_at = Array(n, sint)

    @for_range(n)
    def _(i):
        @for_range(n)
        def _(j):
            match = a[i] == b[j]
            is_match_at[i] += match
            intersection[i] = if_else(match, a[i], intersection[i]) # match * a[i] + (1 - match) * intersection[i]
    return intersection, is_match_at

def square_M(M, n,m):
    M2 = M.copy()
    M2.power(2)
    return M2
            
def bool_M(M, n,m):
    nonzeros = M.nonzero()
    Mb = lil_matrix((n,m), dtype=int)
    for (i,j) in zip(nonzeros[0], nonzeros[1]):
        Mb[i,j] = 1
    return Mb

def write_input_fp(player, value):
    args = ("./gen_input_fp.x")
    popen = subprocess.Popen(args, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    popen.stdin.write("1\n")
    popen.stdin.write("{}\n".format(value))
    popen.wait()
    with open("Player-Data/Private-Input-{}".format(player), "w") as file:
        file.write(popen.stdout.read())

            