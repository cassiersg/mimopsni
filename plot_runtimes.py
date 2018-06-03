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

import numpy as np
from matplotlib import pyplot as plt
import matplotlib2tikz

import runtime_costs

ds = list(range(1, 32))
x = [d+1 for d in ds]
y = []
for d in ds:
    cmimo = runtime_costs.cost_mimo(d)
    cgreedy = runtime_costs.cost_greedy(d)
    cpini1 = runtime_costs.cost_pini1_sbox(d)
    cpini2 = runtime_costs.cost_pini2_sbox(d)
    ctight = runtime_costs.cost_tight(d)
    y.append([
        1,
        cmimo/cgreedy,
        #ctight/cgreedy,
        cpini1/cgreedy,
        cpini2/cgreedy,
        ])
y = np.array(y)
plt.plot(x, y, '.-', markersize=1)
plt.legend([
    'Greedy strategy',
    'MIMO-SNI',
    '\\pinia',
    '\\pinib',
    ])
plt.xlabel('Order $d$')
plt.ylabel('Relative runtime cost')

matplotlib2tikz.save('../dissertation/figs1/runtime_cost_rel.tex',
        figureheight='\\figureheight', figurewidth='\\figurewidth',
        externalize_tables=True, override_externals=True,
        tex_relative_path_to_data='figs1')
plt.show()
