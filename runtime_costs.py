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

import muls_gen
import refs_gen

n_mul = 32
n_refresh = 41
n_refresh_mul = 12
n_mandatory_refresh = n_refresh - n_refresh_mul
n_indep_mul = n_mul - n_refresh_mul
n_refresh_lb = 34


def get_raw_costs(percent_op, percent_rand):
    # rough approximations
    rb = percent_rand/(32*32*(11+16))
    op = percent_op/(32*(6*16+11*3))/32
    return rb, op

raw_costs = get_raw_costs(7.23, 91.91)
#raw_costs = get_raw_costs(25.16, 72.66)
#raw_costs = raw_costs[0], 0 # for randomness complexity


def cost_ni_mul(d, raw_costs=raw_costs):
    # Small cases: Belaid+16
    if 2 <= d <= 4:
        if d == 2: rand, op = 2, 10+9
        elif d == 3: rand, op = 4, 20+16
        elif d == 4: rand, op = 5, 30+25
        rc, oc = raw_costs
        return rc*rand + oc*op
    else:
        return cost_mul(d, 'bbp15', raw_costs)

def cost_sni_ref(d, raw_costs=raw_costs):
    costs = [cost_ref(d, 'bat_ref', raw_costs)]
    try: costs.append(cost_ref(d, 'barthe_ref', raw_costs))
    except ValueError: pass
    return min(costs)

def cost_sni_mul(d, raw_costs=raw_costs):
    return min(
            cost_mul(d, 'isw', raw_costs),
            cost_ni_mul(d, raw_costs) + cost_sni_ref(d, raw_costs)
            )

def cost_pini1_mul(d, raw_costs=raw_costs): return cost_mul(d, 'pini1', raw_costs)
def cost_pini2_mul(d, raw_costs=raw_costs): return cost_mul(d, 'pini2', raw_costs)

def cost_pini3_hp_mul(d, raw_costs=raw_costs): return cost_mul(d, 'pini3_hp', raw_costs)
def cost_pini3_hps_mul(d, raw_costs=raw_costs): return cost_mul(d, 'pini3_hps', raw_costs)

def cost_isw_h_mul(d, raw_costs=raw_costs): return cost_mul(d, 'isw_h', raw_costs)
def cost_isw_hp_mul(d, raw_costs=raw_costs): return cost_mul(d, 'isw_hp', raw_costs)
def cost_isw_hps_mul(d, raw_costs=raw_costs): return cost_mul(d, 'isw_hps', raw_costs)


def cost_mul(d, name, raw_costs=raw_costs):
    return muls_gen.muls[name](d+1).cost(*raw_costs)

def cost_fake_bat_mul(d, raw_costs=raw_costs):
    return muls_gen.fake_bat_mul(d+1, mat_gen=muls_gen.pini_bat_mat_gen).cost(*raw_costs)
def cost_fake_bat_mul_dr(d, raw_costs=raw_costs):
    return muls_gen.fake_bat_mul(d+1, mat_gen=muls_gen.pini_bat_mat_gen_dr).cost(*raw_costs)

def cost_ref(d, name, raw_costs=raw_costs):
    return refs_gen.ref_generator(d+1, refs_gen.refs[name]).cost(*raw_costs)

def cost_greedy(d, raw_costs=raw_costs):
    return n_mul * (cost_sni_ref(d, raw_costs) + cost_sni_mul(d, raw_costs))

def cost_tight(d, raw_costs=raw_costs):
    return n_mul * cost_mul(d, 'isw', raw_costs)

def cost_mimo(d, raw_costs=raw_costs):
    return (
            n_mandatory_refresh*cost_sni_ref(d, raw_costs) +
            n_indep_mul*cost_ni_mul(d, raw_costs) +
            n_refresh_mul*cost_sni_mul(d, raw_costs)
            )

def cost_mimo_h(d, raw_costs=raw_costs, mul=cost_isw_h_mul):
    return (
            n_mandatory_refresh*cost_sni_ref(d, raw_costs) +
            n_indep_mul*mul(d, raw_costs)
            )

def cost_pini1_sbox(d, raw_costs=raw_costs): return n_mul * cost_pini1_mul(d, raw_costs)
def cost_pini2_sbox(d, raw_costs=raw_costs): return n_mul * cost_pini2_mul(d, raw_costs)

def cost_pini_hp_sbox(d, raw_costs=raw_costs): return n_mul * cost_pini_hp_mul(d, raw_costs)
def cost_pini_hps_sbox(d, raw_costs=raw_costs): return n_mul * cost_pini_hps_mul(d, raw_costs)

