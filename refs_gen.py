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

import math
import random

import circuit_model

def simple_ref(circuit, inputs, outputs=None, out_name='sr'):
    d = len(inputs)
    if outputs is None:
        outputs = [circuit.var(f'{out_name}_{i}') for i in range(d)]
    c = circuit
    r = [c.var(f'r_{i}', kind='random') for i in range(d-1)]
    if d == 1:
        c.assign(outputs[0], inputs[0])
    elif d == 2:
        c.l_sum(outputs[0], (inputs[0], r[0]))
        c.l_sum(outputs[1], (inputs[1], r[0]))
    elif d >= 3:
        t = [c.var(f't_{i}') for i in range(d-2)]
        for i in range(d-1):
            c.l_sum(outputs[i], (inputs[i], r[i]))
        c.l_sum(t[0], (inputs[-1], r[0]))
        for i in range(1, d-2):
            c.l_sum(t[i], (t[i-1], r[i]))
        c.l_sum(outputs[d-1], (t[d-3], r[d-2]))
    return outputs

def isw_ref(circuit, inputs, outputs=None, out_name=''):
    d = len(inputs)
    if outputs is None:
        outputs = [circuit.var(f'{out_name}_{i}') for i in range(d)]
    c = [[circuit.var(f'c_{i}_{j}') for j in range(d)] for i in range(d)]
    r = [{j: circuit.var(f'r_{i}_{j}', kind='random') for j in range(i)} for i in range(d)]
    for i in range(d):
        circuit.assign(c[i][0], inputs[i])
        circuit.assign(outputs[i], c[i][d-1])
    for i in range(d):
        for j in range(i):
            circuit.l_sum(c[i][j+1], (c[i][j], r[i][j]))
        for j in range(i+1, d):
            circuit.l_sum(c[i][j], (c[i][j-1], r[j][i]))
    return outputs

def bat_ref_layer(circuit, inputs, outputs, d, d2):
    r = [circuit.var(f'r_{i}', kind='random') for i in range(d2)]
    for i in range(d2):
        circuit.l_sum(outputs[i], (inputs[i], r[i]))
        circuit.l_sum(outputs[d2+i], (inputs[d2+i], r[i]))
    if d % 2 == 1:
        circuit.assign(outputs[d-1], inputs[d-1])

def bat_ref(circuit, inputs, outputs=None, out_name=''):
    d = len(inputs)
    if outputs is None:
        outputs = [circuit.var(f'batref_{out_name}_{i}') for i in range(d)]
    if d == 1:
        circuit.assign(outputs[0], inputs[0])
    elif d == 2:
        r = circuit.var('r', kind='random')
        circuit.l_sum(outputs[0], (inputs[0], r))
        circuit.l_sum(outputs[1], (inputs[1], r))
    else:
        d2 = d//2
        b = [circuit.var(f'b_{i}') for i in range(d)]
        bat_ref_layer(circuit, inputs, b, d, d2)
        c = [circuit.var(f'b_{i}') for i in range(d)]
        bat_ref(circuit, b[:d2], c[:d2])
        bat_ref(circuit, b[d2:], c[d2:])
        bat_ref_layer(circuit, c, outputs, d, d2)
    return outputs

def half_ref(circuit, inputs, outputs=None, out_name=''):
    d = len(inputs)
    if outputs is None:
        outputs = [circuit.var(f'{out_name}_{i}') for i in range(d)]
    if d == 1:
        circuit.assign(outputs[0], inputs[0])
    else:
        d2 = d//2
        bat_ref_layer(circuit, inputs, outputs, d, d2)
    return outputs

def half1_ref(circuit, inputs, outputs=None, out_name=''):
    d = len(inputs)
    if outputs is None:
        outputs = [circuit.var(f'{out_name}_{i}') for i in range(d)]
    if d == 1:
        circuit.assign(outputs[0], inputs[0])
    else:
        d2 = d//2
        if d % 2 == 1:
            r = circuit.var('r', kind='random')
            t = circuit.var('t')
            circuit.l_sum(outputs[d-1], (inputs[d-1], r))
            circuit.l_sum(t, (inputs[0], r))
            inputs = [t] + inputs[1:]
        r = [circuit.var(f'r_{i}', kind='random') for i in range(d2)]
        for i in range(d2):
            circuit.l_sum(outputs[i], (inputs[i], r[i]))
            circuit.l_sum(outputs[d2+i], (inputs[d2+i], r[i]))
    return outputs

def rot_ref(circuit, inputs, outputs=None, out_name=''):
    d = len(inputs)
    if outputs is None:
        outputs = [circuit.var(f'{out_name}_{i}') for i in range(d)]
    if d == 1:
        circuit.assign(outputs[0], inputs[0])
    else:
        randoms = [circuit.var(f'r_{i}', kind='random') for i in range(d)]
        temps = [circuit.var(f'temp_{i}') for i in range(d)]
        for i, r, t in zip(inputs, randoms, temps):
            circuit.l_sum(t, (i, r))
        for o, r, t in zip(outputs, randoms[1:] + [randoms[0]], temps):
            circuit.l_sum(o, (t, r))
    return outputs

def barthe_rd_ref(circuit, inputs, outputs=None, out_name='', n_iter=1):
    tmps = inputs
    for _ in range(n_iter-1):
        tmps = rot_ref(circuit, tmps)
    return rot_ref(circuit, tmps, outputs, out_name)

def barthe_sni_n_rounds(n_shares):
    if n_shares in (3, 4): return 1
    elif n_shares in (5, 6, 7): return 2
    elif n_shares in (8, 9, 10): return 3
    elif n_shares == 11: return 4
    else:
        return math.ceil((n_shares-1)/3) # only conjectured to be SNI
        #raise ValueError('not SNI')

def barthe_ref(circuit, inputs, outputs=None, out_name=''):
    n_rounds = barthe_sni_n_rounds(len(inputs))
    return barthe_rd_ref(circuit, inputs, outputs, out_name, n_rounds)

def empty_ref(circuit, inputs, outputs=None, out_name='sr'):
    d = len(inputs)
    if outputs is None:
        outputs = [circuit.var(f'{out_name}_{i}') for i in range(d)]
    return outputs

def bij_ref(circuit, inputs, outputs=None, out_name='sr'):
    d = len(inputs)
    if outputs is None:
        outputs = [circuit.var(f'{out_name}_{i}') for i in range(d)]
    for i, o in zip(inputs, outputs):
        circuit.assign(o, i)
    return outputs


refs = {
        'simple_ref': simple_ref,
        'SNI_ref': isw_ref,
        'bat_ref': bat_ref,
        'half_ref': half_ref,
        'half1_ref': half1_ref,
        'barthe_ref': barthe_ref,
        'empty_ref': empty_ref,
        'bij_ref': bij_ref,
        }

def ref_generator(d, ref, io_sums=False):
    circuit = circuit_model.Circuit()
    var_inputs = [circuit.var(f'x_{i}', kind='input') for i in range(d)]
    var_outputs = [circuit.var(f'y_{i}', kind='output') for i in range(d)]
    ref(circuit=circuit, inputs=var_inputs, outputs=var_outputs)
    if io_sums:
        s = circuit.var('s')
        circuit.p_sum(s, var_inputs)
        circuit.p_sum(s, var_outputs)
    return circuit


def gen_random_input(d, domain=(0,1)):
    return [random.choice(domain) for i in range(d)]

def test_refresh(d, ref=simple_ref):
    circuit = circuit_model.Circuit()
    var_inputs = [circuit.var(f'x_{i}', kind='input') for i in range(d)]
    var_outputs = [circuit.var(f'y_{i}', kind='output') for i in range(d)]
    ref(circuit=circuit, inputs=var_inputs, outputs=var_outputs)
    g = circuit_model.CompGraph(circuit)
    x = gen_random_input(d)
    inputs = {f'x_{i}': v for i, v in enumerate(x)}
    res, _ = g.compute(inputs)
    y = [v for var, v in res.items() if circuit.vars[var].name.startswith('y_')]
    assert (sum(x) % 2) == (sum(y) % 2)

if __name__ == '__main__':
    import sys
    try:
        d = int(sys.argv[1])
    except IndexError:
        d = 3
    for ref_name, ref_f in refs.items():
    #for ref_name, ref_f in ():
        print(f'---- {ref_name}, d={d} ----')
        circuit = circuit_model.Circuit()
        var_inputs = [circuit.var(f'x_{i}', kind='input') for i in range(d)]
        ref_f(circuit, var_inputs, out_name='y')
        print(circuit)
        for _ in range(100):
            test_refresh(d, ref_f)

