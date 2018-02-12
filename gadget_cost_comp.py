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

def ni_mul(d):
    """Belaid et al."""
    return int(d**2/4)+d

def sni_mul(d):
    """ISW"""
    return int(d*(d+1)/2)

def sni_ref(d):
    """Batistello"""
    return sni_ref_rec(d+1)

def sni_ref_rec(n):
    if n == 1:
        return 0
    elif n == 2:
        return 1
    else:
        return 2*(n//2) + sni_ref_rec(n//2) + sni_ref_rec(int(ceil(n/2)))

def test_sni_ref():
    """Compare general recursive function with formula computed by hand for powers of 2"""
    for i in range(1, 10):
        d = 2**i-1
        a = sni_ref(d)
        b = int((d+1)*(log2(d+1)-1)+(d+1)/2)
        assert a==b, (d, a, b)

def pini_mul(d):
    """PINI mul, randomness identical to ISW"""
    return sni_mul(d)

# test
test_sni_ref()

comp_better_isw = next(d for d in range(1, 100) if ni_mul(d) + sni_ref(d) <= sni_mul(d))
print('miniumum d for which (ni mul + sni ref) better than ISW:', comp_better_isw)

print('all d for which pini is better than mimo-sni (considering only ISW, Belaid and Batistello gadgets, for optimized S-Box with 41 refresh elements:',
        [d for d in range(1, 100) if 32*pini_mul(d) <= min(41*sni_ref(d)+32*ni_mul(d), (41-32)*sni_ref(d) + 32*sni_mul(d))])

print('Battistello refresh (d, cost):')
pprint([(d, sni_ref(d)) for d in range(1, 30)])

