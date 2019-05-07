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
"""

from matplotlib import pyplot as plt

import gad_costs


class OpCost:
    def __init__(self, ands, xors, refs):
        self.ands = ands
        self.xors = xors
        self.refs = refs

    def __add__(self, other):
        return OpCost(self.ands+other.ands, self.xors+other.xors, self.refs+other.refs)

    def __mul__(self, other):
        return OpCost(other*self.ands, other*self.xors, other*self.refs)
    def __rmul__(self, other):
        return self.__mul__(other)

    def double_sni(self):
        return OpCost(self.ands, self.xors, self.ands)

    def naive(self):
        return OpCost(self.ands, self.xors, self.xors)

    def erase_ref(self):
        return OpCost(self.ands, self.xors, 0)

    def gates(self, mul, xor, ref):
        return self.ands*mul + self.xors*xor + self.refs*ref

class BCipher:
    def __init__(self, block_size, sbox_size, k_sched_sbox, k_sched_xor,
            sbox_and, sbox_xor, sbox_ref, lin_xor, n_rounds):
        """ lin_xor: excluding key addition"""
        self.block_size = block_size
        self.sbox_size = sbox_size
        self.k_sched_sbox = k_sched_sbox
        self.k_sched_xor = k_sched_xor
        self.sbox_and = sbox_and
        self.sbox_xor = sbox_xor
        self.sbox_ref = sbox_ref
        self.lin_xor = lin_xor
        self.n_rounds = n_rounds

    def n_sbox(self):
        return self.block_size // self.sbox_size

    def cost_sbox(self):
        return OpCost(self.sbox_and, self.sbox_xor, self.sbox_ref)

    def cost_round(self):
        c = self.n_sbox()*self.cost_sbox()
        c.xors += self.lin_xor + self.block_size
        return c

    def cost_round_ksched(self):
        c = self.k_sched_sbox * self.cost_sbox()
        c.xors += self.k_sched_xor
        c.refs += self.block_size - self.sbox_size*self.k_sched_sbox
        return c

    def cost(self):
        return self.n_rounds * (self.cost_round() + self.cost_round_ksched())


FantomasCipher = BCipher(
    block_size = 128,
    sbox_size = 8,
    k_sched_sbox = 0,
    k_sched_xor = 0,
    sbox_xor = 30,
    sbox_and = 11,
    sbox_ref = 8,
    lin_xor = 64+1,
    n_rounds = 12,
)

NoekeonCipher = BCipher(
        block_size = 128,
        sbox_size = 4,
        k_sched_sbox = 0,
        k_sched_xor = 0,
        sbox_xor = 7+6,
        sbox_and=4,
        sbox_ref = 2,
        lin_xor = 128*6,
        n_rounds = 16,
)

PresentCipher = BCipher(
        block_size = 64,
        sbox_size = 4,
        k_sched_sbox = 1,
        k_sched_xor = 4,
        sbox_xor = 9+7,
        sbox_and=4,
        sbox_ref = 4,
        lin_xor = 64,
        n_rounds = 31,
)

### MixColumns
xtime = 4
xt_mc = 4*xtime
sum_mc = 3*8
sums_mc = 4*(2*8)
mc_tot = 4*(xt_mc + sum_mc + sums_mc)
AESCipher = BCipher(
    block_size = 128,
    sbox_size = 8,
    k_sched_sbox = 4,
    k_sched_xor = 32+128,
    sbox_xor = 23+30+30,
    sbox_and = 32,
    sbox_ref = 0,
    lin_xor = mc_tot,
    n_rounds = 10,
)


def aes_mimo_sni(c, d):
    ands = (AESCipher.k_sched_sbox + AESCipher.n_sbox())*AESCipher.sbox_and
    xors = (AESCipher.k_sched_sbox + AESCipher.n_sbox())*AESCipher.sbox_xor + AESCipher.lin_xor + 128 + AESCipher.k_sched_xor
    refs = 41*(AESCipher.k_sched_sbox + AESCipher.n_sbox())
    return (AESCipher.n_rounds*OpCost(ands, xors, refs)).gates(
            gad_costs.ni_mul(d), gad_costs.Cost(0, d, 0), gad_costs.ref(d))


def double_sni(cipher, d):
    return cipher.cost().double_sni().gates(
            gad_costs.sni_mul(d),
            gad_costs.Cost(0, d, 0),
            gad_costs.ref(d)
            )

def pini1(cipher, d):
    return cipher.cost().erase_ref().gates(
            gad_costs.pini1(d),
            gad_costs.Cost(0, d, 0),
            gad_costs.Cost(0, 0, 0),
            )

def pini2(cipher, d):
    return cipher.cost().erase_ref().gates(
            gad_costs.pini2(d),
            gad_costs.Cost(0, d, 0),
            gad_costs.Cost(0, 0, 0),
            )

def naive(cipher, d):
    return cipher.cost().naive().gates(
            gad_costs.sni_mul(d),
            gad_costs.Cost(0, d, 0),
            gad_costs.ref(d)
            )

def tpc(cipher, d):
    return cipher.cost().gates(
            gad_costs.sni_mul(d),
            gad_costs.Cost(0, d, 0),
            gad_costs.ref(d)
            )

### Plot
rand_ratio = 80
costs = (rand_ratio, 1, 1)

methods = [
        ("Double-SNI", double_sni),
        ("TPC", tpc),
        ("Naive", naive),
        ("PINI1", pini1),
        ("PINI2", pini2),
        ]

ciphers = [
        ("AES", AESCipher, methods + [("MIMO-SNI", aes_mimo_sni)]),
        ("Fantomas", FantomasCipher, methods),
        ("Noekeon", NoekeonCipher, methods),
        ("Present", PresentCipher, methods),
        ]

ds = list(range(2, 33))

for c_name, cipher, m_methods in ciphers:
    cycles = [[m(cipher, d).compress(*costs) for d in ds] for _, m in m_methods]
    plt.figure()
    for p in cycles:
        plt.loglog(ds, p, '.-', basex=2, basey=2, markersize=2)
    plt.legend([m for m, _ in m_methods])
    plt.xlabel('$d$')
    plt.ylabel('Cost')
    plt.title(c_name)


tikz = False 
#tikz = True
if tikz:
    import matplotlib2tikz
    matplotlib2tikz.save(
            '../SNI_opt/v2/figs/run_cost.tex',
            figureheight='\\figureheight',
            figurewidth='\\figurewidth',
            externalize_tables=True,
            override_externals=True,
            tex_relative_path_to_data='figs',
            )

plt.show()
