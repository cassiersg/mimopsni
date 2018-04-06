#! /usr/bin/python3

# Copyright 2018 Gaëtan Cassiers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Comparison of cost of implementation of bitslice AES using generic
multiplication and refresh gadgets, as a function of the security order.
"""

from math import log2, ceil
from pprint import pprint

import numpy as np
import pandas as pd

import matplotlib2tikz

n_mul = 32
n_refresh = 41
n_refresh_mul = 12
n_mandatory_refresh = n_refresh - n_refresh_mul
n_indep_mul = n_mul - n_refresh_mul
n_refresh_lb = 34

def bel_mul(d):
    """NI mul from Belaid et al."""
    return int(d**2/4)+d

def ni_mul(d):
    # Small cases: Belaid+16
    if d == 2: return 2
    elif d == 3: return 4
    elif d == 4: return 5
    else: return bel_mul(d)

def isw_mul(d):
    """ISW"""
    return int(d*(d+1)/2)

def barthe_sni_refresh(d):
    "Barthe+17"
    if d == 3: return 4
    elif d == 5: return 12
    elif d == 6: return 14
    elif d == 7: return 24
    elif d == 8: return 27
    elif d == 9: return 30
    elif d == 10: return 40
    else: return float('inf')

def barthe_sni_mul(d):
    "Barthe+17"
    if d == 7: return 24
    else: return float('inf')

def sni_mul(d):
    return min(barthe_sni_mul(d), isw_mul(d), ni_mul(d) + sni_ref(d))

def bat_ref(d):
    """Batistello refresh"""
    return bat_ref_rec(d+1)

def bat_ref_rec(n):
    if n == 1:
        return 0
    elif n == 2:
        return 1
    else:
        return 2*(n//2) + bat_ref_rec(n//2) + bat_ref_rec(int(ceil(n/2)))

def test_bat_ref():
    """Compare general recursive function with formula computed by hand for powers of 2"""
    for i in range(1, 10):
        d = 2**i-1
        a = bat_ref(d)
        b = int((d+1)*(log2(d+1)-1)+(d+1)/2)
        assert a==b, (d, a, b)

def sni_ref(d):
    return min(barthe_sni_refresh(d), bat_ref(d))

def pini_mul(d):
    """PINI mul, randomness identical to ISW"""
    return isw_mul(d)

def pini_mul2(d):
    """PINI improved"""
    return bel_mul(d) + (d+1)

# test
test_bat_ref()


def s_box_greedy(d):
    return n_mul * (sni_ref(d) + sni_mul(d))

def s_box_mimo(d):
    return n_mandatory_refresh*sni_ref(d) + n_indep_mul*ni_mul(d) + n_refresh_mul*sni_mul(d)

def s_box_mimo_lb(d):
    return (n_refresh_lb-n_mul)*sni_ref(d) + n_mul*sni_mul(d)

def s_box_pini(d):
    return 32*pini_mul(d)

def s_box_pini2(d):
    return 32*pini_mul2(d)


table = [(d+1, s_box_greedy(d), s_box_mimo(d), s_box_pini(d), s_box_pini2(d)) for d in range(5, 32)]
table = [(o, g, m, p, p2, m/g, p/g, p2/g) for o, g, m, p, p2 in table]
table = pd.DataFrame(table, columns=['d', 'greedy', 'MIMO-SNI (best case)', 'PINI', 'PINI2*', 'MIMO/greedy', 'PINI/greedy', 'PINI2/greedy'], index=None)
#pprint(table)
print('Number of random bits')
print(table.to_string(index=False))
print('*PINI2: based no Belaïd et al., not in paper')

comp_better_isw = next(d for d in range(1, 100) if ni_mul(d) + sni_ref(d) <= sni_mul(d))
print('miniumum d for which (ni mul + sni ref) better than ISW:', comp_better_isw)

print('all d for which pini is better than mimo-sni (considering only ISW, Belaid and Batistello gadgets, for optimized S-Box with 41 refresh elements:',
        [d for d in range(1, 100) if 32*pini_mul(d) <= min(41*sni_ref(d)+32*ni_mul(d), (41-32)*sni_ref(d) + 32*sni_mul(d))])

print('Battistello refresh (d, cost):')
pprint([(d, bat_ref(d), barthe_sni_refresh(d), isw_mul(d)) for d in range(1, 30)])
print('SNI mul (d, isw, barthe, ni+ref)')
pprint([(d, isw_mul(d), barthe_sni_mul(d), sni_ref(d)+ni_mul(d), bel_mul(d)) for d in range(1, 30)])

import matplotlib.pyplot as plt

ds = list(range(1, 32))
x = [d+1 for d in ds]
y = np.array([[
    #d+1,
    s_box_greedy(d),
    s_box_mimo(d),
    s_box_pini(d),
    #s_box_pini2(d)
    ] for d in ds])
plt.semilogy(x, y, '.-')
plt.legend(['Greedy strategy', 'MIMO-SNI', 'PINI',])
plt.xlabel('Order $d$')
plt.ylabel('Randomness cost (bits)')
#matplotlib2tikz.save('../SNI_opt/figs/rand_cost.tex', figureheight='\\figureheight', figurewidth='\\figurewidth')
plt.show()
y2 = np.array([[
    1,
    s_box_mimo(d)/ s_box_greedy(d),
    s_box_pini(d)/ s_box_greedy(d),
    ] for d in ds])
plt.plot(x, y2, '.-')
plt.legend(['Greedy strategy', 'MIMO-SNI', 'PINI',])
plt.xlabel('Order $d$')
plt.ylabel('Relative randomness cost')
#matplotlib2tikz.save('../SNI_opt/figs/rand_cost_rel.tex', figureheight='\\figureheight', figurewidth='\\figurewidth')
plt.show()

