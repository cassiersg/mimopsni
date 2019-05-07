class Cost:
    def __init__(self, rand, sums, prod):
        self.rand = rand; self.sums=sums; self.prod=prod;
    def __add__(self, other):
        return Cost(self.rand+other.rand, self.sums+other.sums, self.prod+other.prod)
    def __mul__(self, other):
        return Cost(self.rand*other, self.sums*other, self.prod*other)
    def __rmul__(self, other):
        return self.__mul__(other)
    def __repr__(self):
        return "Cost({}, {}, {})".format(self.rand, self.sums, self.prod)
    def compress(self, rand, sums, prod):
        return self.rand*rand + self.sums*sums + self.prod*prod

# REM: d == # of shares

def mul_from_rand(d, rand):
    return Cost(rand, d*(d-1)+2*rand, d*d)

def ni_mul_rand(d):
    """NI mul from Belaid et al."""
    if d == 3:
        rand = 2
    elif d == 4:
        rand = 4
    elif d == 5:
        rand = 5
    else:
        rand = int((d-1)**2/4)+d-1
    return rand

def isw_mul_rand(d):
    """ISW"""
    rand = int(d*(d-1)/2)
    return rand

def ref_rand(d):
    """from Barthe et al., Improved Parallel Mask Refreshing Algorithms"""
    rands = [None, 0, 1, 3, 4, 8, 12, 13, 16, 18, 20, 22, 24, 26, 28, 30, 32,
            34, 35, 38]
    if d < len(rands):
        return rands[d]
    else:
        return 2*(d//2)+ref_rand(d//2)+ref_rand(d-d//2)

def barthe_sni_mul_rand(d):
    "Barthe+17"
    if d == 8: return 24
    else: return float('inf')

def sni_mul_rand(d):
    return min(isw_mul_rand(d), ni_mul_rand(d)+ref_rand(d), barthe_sni_mul_rand(d))

def pini1_rand(d):
    return isw_mul_rand(d)

def pini2_rand(d):
    return int((d-1)**2/4)+2*d-1

def pini1(d):
    rand = pini1_rand(d)
    n_shared_muls = d*(d-1)
    return Cost(rand, d+2*n_shared_muls+2*rand, 2*n_shared_muls+d)

def pini2(d):
    rand = pini2_rand(d)
    n_shared_muls = d*(d-1)
    return Cost(rand, 4*n_shared_muls+2*rand, 2*n_shared_muls+d)


def ni_mul(d):
    return mul_from_rand(d, ni_mul_rand(d))
def ni_isw(d):
    return mul_from_rand(d, isw_mul_rand(d))
def sni_mul(d):
    return mul_from_rand(d, sni_mul_rand(d))
def ref(d):
    rand = ref_rand(d)
    return Cost(rand, 2*rand, 0)

if __name__ == '__main__':
    ds = [2, 3, 4, 5, 6, 7, 8, 16, 32]
    gadgets = [
            ("SNI refresh", ref),
            ("NI mul.", ni_mul),
            ("SNI mul.", sni_mul),
            ("$\\mathsf{PINI}_1$ mul.", pini1),
            ("$\\mathsf{PINI}_2$ mul.", pini2),
            ]
    columns = ["d"] + [n for n, _ in gadgets]

    table_rand = [[d]+[g(d).rand for _, g in gadgets] for d in ds]
    table_sums = [[d]+[g(d).sums for _, g in gadgets] for d in ds]
    table_prod = [[d]+[g(d).prod for _, g in gadgets] for d in ds]

    import pandas as pd

    table_rand = pd.DataFrame(table_rand, columns=columns, index=None)
    table_sums = pd.DataFrame(table_sums, columns=columns, index=None)
    table_prod = pd.DataFrame(table_prod, columns=columns, index=None)

    print(table_rand)
    print(table_sums)
    print(table_prod)
    print(table_rand.to_latex(index=False, escape=False))
    print(table_sums.to_latex(index=False, escape=False))
    print(table_prod.to_latex(index=False, escape=False))
