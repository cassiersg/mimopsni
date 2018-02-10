
from math import log2
from pprint import pprint

def ni_mul(d):
    """Belaid et al."""
    return int(d**2/4)+d

def sni_mul(d):
    """ISW"""
    return int(d*(d+1)/2)

def sni_ref(d):
    """Batistello"""
    return int((d+1)*log2(d+1))

def pini_mul(d):
    """PINI mul"""
    return sni_mul(d)

comp_better_isw = next(d for d in range(1, 100) if ni_mul(d) + sni_ref(d) <= sni_mul(d))
print('min d for which (ni mul + sni ref) better than ISW:', comp_better_isw)

print('d for which pini is better than mimo-sni')
pprint([d for d in range(1, 100) if 32*pini_mul(d) <= min(41*sni_ref(d)+32*ni_mul(d), (41-32)*sni_ref(d) + 32*sni_mul(d))])

