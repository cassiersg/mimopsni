
import itertools as it
import functools as ft
import random

import circuit_model
import refs_gen

def mul_preamble(d, c, x_name='x', y_name='y', z_name='z'):
    x = c.var(x_name, continuous=True, kind='output')
    y = c.var(y_name, kind='output')
    z = c.var(z_name, kind='output')
    c.bij(x, y)
    c.bij(x, z)
    sh_x, sh_y, sh_z = [], [], []
    for i in range(d):
        sh_x.append(c.var(f'{x_name}_{i}', kind='input'))
        sh_y.append(c.var(f'{y_name}_{i}', kind='input'))
        sh_z.append(c.var(f'{z_name}_{i}', kind='output'))
    if d == 1:
        c.bij(x, sh_x[0])
        c.bij(y, sh_y[0])
        c.bij(z, sh_z[0])
    else:
        c.p_sum(x, sh_x)
        c.p_sum(y, sh_y)
        c.p_sum(z, sh_z)
    return x, y, z, sh_x, sh_y, sh_z

def mat_prod(c, in_x, in_y, ref, var_sums, dr):
    if ref is None:
        return [[(ix, iy) for iy in in_y] for ix in in_x]

    nx = len(in_x)
    ny = len(in_y)
    if nx == 1 and ny == 1:
        if var_sums is not None:
            x_sum, y_sum = var_sums
            # Redundant, already covered
            #c.p_bij(in_x[0], x_sum)
            #c.p_bij(in_y[0], y_sum)
        return [[(in_x[0], in_y[0])]]
    if nx == 1:
        assert ny <= 2
        if var_sums is not None:
            x_sum, y_sum = var_sums
            # Redundant, already covered
            #c.p_bij(in_x[0], x_sum)
            c.p_sum(y_sum, in_y)
        return [[(in_x[0], iy) for iy in in_y]]
    elif ny == 1:
        assert nx <= 2
        if var_sums is not None:
            x_sum, y_sum = var_sums
            # Redundant, already covered
            #c.p_bij(in_y[0], y_sum)
            c.p_sum(x_sum, in_x)
        return [[(ix, in_y[0])] for ix in in_x]
    else:
        nx2 = nx//2
        ny2 = ny//2
        in_x1 = in_x[:nx2]
        in_x2 = in_x[nx2:]
        in_y1 = in_y[:ny2]
        in_y2 = in_y[ny2:]
        if var_sums is not None:
            x_sum, y_sum = var_sums
            x_half1 = c.var('tmp_sum_x1')
            x_half2 = c.var('tmp_sum_x2')
            y_half1 = c.var('tmp_sum_y1')
            y_half2 = c.var('tmp_sum_y2')
            c.p_sum(x_sum, (x_half1, x_half2))
            c.p_sum(y_sum, (y_half1, y_half2))
            c.p_sum(x_half1, in_x1)
            c.p_sum(x_half2, in_x2)
            c.p_sum(y_half1, in_y1)
            c.p_sum(y_half2, in_y2)
            sum11 = (x_half1, y_half1)
            sum12 = (x_half1, y_half2)
            sum21 = (x_half2, y_half1)
            sum22 = (x_half2, y_half2)
        else:
            sum11 = sum12 = sum21 = sum22 = None
        if dr:
            in_x1_1 = ref(c, in_x1)
            in_y1_1 = ref(c, in_y1)
            in_x2_1 = ref(c, in_x2)
            in_y2_1 = ref(c, in_y2)
        else:
            in_x1_1 = in_x1
            in_y1_1 = in_y1
            in_x2_1 = in_x2
            in_y2_1 = in_y2
        in_x1_2 = ref(c, in_x1)
        in_y1_2 = ref(c, in_y1)
        in_x2_2 = ref(c, in_x2)
        in_y2_2 = ref(c, in_y2)
        m11 = mat_prod(c, in_x1_1, in_y1_1, ref, sum11, dr)
        m12 = mat_prod(c, in_x1_2, in_y2_1, ref, sum12, dr)
        m21 = mat_prod(c, in_x2_1, in_y1_2, ref, sum21, dr)
        m22 = mat_prod(c, in_x2_2, in_y2_2, ref, sum22, dr)
        return ([o1+o2 for o1, o2 in zip(m11, m12)] +
                [o1+o2 for o1, o2 in zip(m21, m22)])

def BBP15(d):
    d2 = d-1
    c = circuit_model.Circuit()
    _, _, _, x, y, z = mul_preamble(d, c)

    # product matrix
    p = [[c.var(f'p_{i}_{j}') for j in range(d)] for i in range(d)]
    for i, j in it.product(range(d), range(d)):
        c.l_prod(p[i][j], (x[i], y[j]))

    # randoms & temps in matrix & compression
    r = [
            {d2-j: c.var(f'r_{i}_{j}', kind='random') for j in range(0, d2-i, 2)}
            for i in range(d)
            ]
    r2 = {j: c.var(f'r2_{j}', kind='random') for j in range(d2-1, 0, -2)}
    t = [
            {j: [c.var(f't_{i}_{j}_{k}') for k in range(5)]
                    for j in range(d2, i+1, -2)}
            for i in range(d)
            ]
    c_var = [{j: c.var(f'c_{i}_{j}') for j in range(d2+2, i+1, -2)}
            for i in range(d)
            ]
    for i in range(d):
        c.bij(c_var[i][d2+2], p[i][i])
        for j in range(d2, i+1, -2):
            c.l_sum(t[i][j][0], (r[i][j], p[i][j]))
            c.l_sum(t[i][j][1], (t[i][j][0], p[j][i]))
            c.l_sum(t[i][j][2], (t[i][j][1], r2[j-1]))
            c.l_sum(t[i][j][3], (t[i][j][2], p[i][j-1]))
            c.l_sum(t[i][j][4], (t[i][j][3], p[j-1][i]))
            c.l_sum(c_var[i][j], (c_var[i][j+2], t[i][j][4]))
        if (i-d2) % 2 != 0:
            t[i][i+1] = [c.var(f't_{i}_{i+1}_0'), c.var(f't_{i}_{i+1}_1')]
            c_var[i][i+1] = c.var(f'c_{i}_{i+1}')
            c.l_sum(t[i][i+1][0], (r[i][i+1], p[i][i+1]))
            c.l_sum(t[i][i+1][1], (t[i][i+1][0], p[i+1][i]))
            c.l_sum(c_var[i][i+1], (c_var[i][i+3], t[i][i+1][1]))
            if i % 2 == 1:
                c.l_sum(z[i], (c_var[i][i+1], r2[i]))
            else:
                c.bij(z[i], c_var[i][i+1])
        else:
            for j in range(i-1, -1, -1):
                c_var[i][j+2] = c.var(f'c_{i}_{j+2}')
                c.l_sum(c_var[i][j+2], (c_var[i][j+3], r[j][i]))
            c.bij(z[i], c_var[i][2])

    return c

def pini2(d, mat_gen, tmp_sums):
    d2 = d-1
    c = circuit_model.Circuit()
    sx, sy, sz, x, y, z = mul_preamble(d, c)

    if tmp_sums:
        var_sums = (sx, sy)
    else:
        var_sums = None
    ref_prods = mat_gen(c, x, y, var_sums=var_sums)

    # product matrix
    s1 = [c.var(f's1_{i}', kind='random') for i in range(d)]
    s = [{j: c.var(f's_{i}_{j}') for j in range(i+1, d)} for i in range(d)]
    u = [{j: [c.var(f's_{i}_{j}_{k}') for k in range(2)]
        for j in range(i+1, d)} for i in range(d)]
    p = [{j: [c.var(f's_{i}_{j}_{k}') for k in range(4)]
        for j in range(i+1, d)} for i in range(d)]
    for i in range(d):
        for j in range(i+1, d):
            c.l_sum(s[i][j], (s1[i], s1[j]))
            xi, yj = ref_prods[i][j]
            xj, yi = ref_prods[j][i]
            c.l_sum(u[i][j][0], (yj, s[i][j]))
            c.l_sum(u[i][j][1], (xj, s[i][j]))
            c.l_prod(p[i][j][0], (xi, s[i][j]))
            c.l_prod(p[i][j][1], (xi, u[i][j][0]))
            c.l_prod(p[i][j][2], (yi, s[i][j]))
            c.l_prod(p[i][j][3], (yi, u[i][j][1]))

    # randoms & temps in matrix & compression
    r = [
            {d2-j: c.var(f'r_{i}_{j}', kind='random') for j in range(0, d2-i, 2)}
            for i in range(d)
            ]
    r2 = {j: c.var(f'r2_{j}', kind='random') for j in range(d2-1, 0, -2)}
    t = [
            {j: [c.var(f't_{i}_{j}_{k}') for k in range(9)]
                    for j in range(d2, i+1, -2)}
            for i in range(d)
            ]
    c_var = [{j: c.var(f'c_{i}_{j}') for j in range(d2+2, i+1, -2)}
            for i in range(d)
            ]
    for i in range(d):
        pi = c.var(f'p_{i}_{i}')
        c.l_prod(pi, ref_prods[i][i])
        c.bij(c_var[i][d2+2], pi)
        for j in range(d2, i+1, -2):
            c.l_sum(t[i][j][0], (r[i][j], p[i][j][0]))
            c.l_sum(t[i][j][1], (t[i][j][0], p[i][j][1]))
            c.l_sum(t[i][j][2], (t[i][j][1], p[i][j][2]))
            c.l_sum(t[i][j][3], (t[i][j][2], p[i][j][3]))
            c.l_sum(t[i][j][4], (t[i][j][3], r2[j-1]))
            c.l_sum(t[i][j][5], (t[i][j][4], p[i][j-1][0]))
            c.l_sum(t[i][j][6], (t[i][j][5], p[i][j-1][1]))
            c.l_sum(t[i][j][7], (t[i][j][6], p[i][j-1][2]))
            c.l_sum(t[i][j][8], (t[i][j][7], p[i][j-1][3]))
            c.l_sum(c_var[i][j], (c_var[i][j+2], t[i][j][8]))
        if (i-d2) % 2 != 0:
            t[i][i+1] = [c.var(f't_{i}_{i+1}_{k}') for k in range(4)]
            c_var[i][i+1] = c.var(f'c_{i}_{i+1}')
            c.l_sum(t[i][i+1][0], (r[i][i+1], p[i][i+1][0]))
            c.l_sum(t[i][i+1][1], (t[i][i+1][0], p[i][i+1][1]))
            c.l_sum(t[i][i+1][2], (t[i][i+1][1], p[i][i+1][2]))
            c.l_sum(t[i][i+1][3], (t[i][i+1][2], p[i][i+1][3]))
            c.l_sum(c_var[i][i+1], (c_var[i][i+3], t[i][i+1][3]))
            if i % 2 == 1:
                c.l_sum(z[i], (c_var[i][i+1], r2[i]))
            else:
                c.bij(z[i], c_var[i][i+1])
        else:
            for j in range(i-1, -1, -1):
                c_var[i][j+2] = c.var(f'c_{i}_{j+2}')
                c.l_sum(c_var[i][j+2], (c_var[i][j+3], r[j][i]))
            c.bij(z[i], c_var[i][2])

    return c

def pini1(d):
    c = circuit_model.Circuit()
    sx, sy, sz, x, y, z = mul_preamble(d, c)

    # randoms & temps in matrix
    r = [{j: c.var(f'r_{i}_{j}', kind='random' if j < i else 'intermediate')
        for j in range(d) if j != i}
        for i in range(d)]
    for i in range(d):
        for j in range(i):
            c.bij(r[j][i], r[i][j])

    s = [{j: c.var(f's_{i}_{j}') for j in range(d) if j != i}
            for i in range(d)]
    p = [{j: [c.var(f'p_{i}_{j}_{k}') for k in range(2)]
        for j in range(d) if j != i}
        for i in range(d)]
    t = [{j: c.var(f't_{i}_{j}') for j in range(d)}
            for i in range(d)]
    for i in range(d):
        c.l_prod(t[i][i], (x[i], y[i]))
        # not(x_i)
        nxi = c.var(f'nxi_{i}_{j}')
        c.l_sum(nxi, (x[i],))
        for j in range(d):
            if j != i:
                xi, yj = x[i], y[j]
                c.l_sum(s[i][j], (yj, r[i][j]))
                c.l_prod(p[i][j][0], (nxi, r[i][j]))
                c.l_prod(p[i][j][1], (xi, s[i][j]))
                c.l_sum(t[i][j], (p[i][j][0], p[i][j][1]))

    c_var = [[c.var(f'c_{i}_{j}') for j in range(d)] for i in range(d)]
    for i in range(d):
        c.bij(c_var[i][0], t[i][0])
        for j in range(1, d):
            c.l_sum(c_var[i][j], (c_var[i][j-1], t[i][j]))
        c.bij(z[i], c_var[i][d-1])

    return c

def pini3(d, mat_gen, tmp_sums):
    c = circuit_model.Circuit()
    sx, sy, sz, x, y, z = mul_preamble(d, c)

    if tmp_sums:
        var_sums = (sx, sy)
    else:
        var_sums = None
    ref_prods = mat_gen(c, x, y, var_sums=var_sums)


    # randoms & temps in matrix
    r = [{j: c.var(f'r_{i}_{j}', kind='random' if j < i else 'intermediate')
        for j in range(d) if j != i}
        for i in range(d)]
    for i in range(d):
        for j in range(i):
            c.bij(r[j][i], r[i][j])

    s = [{j: c.var(f's_{i}_{j}') for j in range(d) if j != i}
            for i in range(d)]
    p = [{j: [c.var(f'p_{i}_{j}_{k}') for k in range(3)]
        for j in range(d) if j != i}
        for i in range(d)]
    t = [{j: c.var(f't_{i}_{j}') for j in range(d)}
            for i in range(d)]
    for i in range(d):
        c.l_prod(t[i][i], ref_prods[i][i])
        for j in range(d):
            if j != i:
                xi, yj = ref_prods[i][j]
                # not(x_i)
                #nxi = c.var(f'nxi_{i}_{j}')
                #c.l_sum(nxi, (xi,))
                c.l_sum(s[i][j], (yj, r[i][j]))
                c.l_prod(p[i][j][0], (xi, r[i][j]))
                c.l_prod(p[i][j][1], (xi, s[i][j]))
                c.l_sum(p[i][j][2], (p[i][j][0], r[i][j]))
                c.l_sum(t[i][j], (p[i][j][2], p[i][j][1]))

    c_var = [[c.var(f'c_{i}_{j}') for j in range(d)] for i in range(d)]
    for i in range(d):
        c.bij(c_var[i][0], t[i][0])
        for j in range(1, d):
            c.l_sum(c_var[i][j], (c_var[i][j-1], t[i][j]))
        c.bij(z[i], c_var[i][d-1])

    return c

def bat_mul(d, mat_gen, tmp_sums):
    c = circuit_model.Circuit()
    sx, sy, sz, x, y, z = mul_preamble(d, c)

    if tmp_sums:
        var_sums = (sx, sy)
    else:
        var_sums = None
    # product matrix
    ref_prods = mat_gen(c, x, y, var_sums=var_sums)

    p = [[c.var(f's_{i}_{j}') for j in range(d)] for i in range(d)]
    for i in range(d):
        for j in range(d):
            c.l_prod(p[i][j], ref_prods[i][j])
    r = [{j: c.var(f'r_{i}_{j}', kind='random') for j in range(i+1, d)}
            for i in range(d)]
    t = [{j: c.var(f't_{i}_{j}') for j in range(i+1, d)}
            for i in range(d)]
    s = [[c.var(f's_{i}_{j}') for j in range(d)]
            for i in range(d)]
    c_var = [[c.var(f's_{i}_{j}') for j in range(d)]
            for i in range(d)]
    for i in range(d):
        for j in range(i+1, d):
            c.bij(s[i][j], r[i][j])
            c.l_sum(t[i][j], (r[i][j], p[i][j]))
            c.l_sum(s[j][i], (t[i][j], p[j][i]))
    for i in range(d):
        c.bij(s[i][i], p[i][i])
        c.bij(c_var[i][0], s[i][0])
        for j in range(1, d):
            c.l_sum(c_var[i][j], (c_var[i][j-1], s[i][j]))
        c.bij(z[i], c_var[i][d-1])

    return c

def fake_bat_mul(d, mat_gen):
    c = circuit_model.Circuit()
    sx, sy, sz, x, y, z = mul_preamble(d, c)

    if tmp_sums:
        var_sums = (sx, sy)
    else:
        var_sums = None
    # product matrix
    ref_prods = mat_gen(c, x, y)

    return c

mat_prod_0 = ft.partial(mat_prod,
        ref=None, var_sums=None, dr=False)
mat_prod_h = ft.partial(mat_prod,
        ref=refs_gen.bat_ref, var_sums=None, dr=False)
mat_prod_hs = ft.partial(mat_prod,
        ref=refs_gen.simple_ref, var_sums=None, dr=False)
mat_prod_hp = ft.partial(mat_prod,
        ref=refs_gen.bat_ref, var_sums=None, dr=True)
mat_prod_hps = ft.partial(mat_prod,
        ref=refs_gen.simple_ref, var_sums=None, dr=True)
mat_prod_hpe = ft.partial(mat_prod,
        ref=refs_gen.empty_ref, var_sums=None, dr=True)
mat_prod_hpb = ft.partial(mat_prod,
        ref=refs_gen.bij_ref, var_sums=None, dr=True)

muls = {
        'bbp15': BBP15,
        'isw': ft.partial(bat_mul, mat_gen=mat_prod_0, tmp_sums=True),
        'isw_h': ft.partial(bat_mul, mat_gen=mat_prod_h, tmp_sums=True),
        'isw_hp': ft.partial(bat_mul, mat_gen=mat_prod_hp, tmp_sums=True),
        'isw_hs': ft.partial(bat_mul, mat_gen=mat_prod_hs, tmp_sums=True),
        'isw_hps': ft.partial(bat_mul, mat_gen=mat_prod_hps, tmp_sums=True),
        #'isw_hpe': ft.partial(bat_mul, mat_gen=mat_prod_hpe, tmp_sums=True),
        #'isw_hpb': ft.partial(bat_mul, mat_gen=mat_prod_hpb, tmp_sums=True),
        'isw_ht': ft.partial(bat_mul, mat_gen=mat_prod_h, tmp_sums=False),
        'isw_hpt': ft.partial(bat_mul, mat_gen=mat_prod_hp, tmp_sums=False),
        'pini1': pini1,
        'pini3': ft.partial(pini3, mat_gen=mat_prod_0, tmp_sums=True),
        'pini3h': ft.partial(pini3, mat_gen=mat_prod_h, tmp_sums=True),
        'pini3hp': ft.partial(pini3, mat_gen=mat_prod_hp, tmp_sums=True),
        'pini3hs': ft.partial(pini3, mat_gen=mat_prod_hs, tmp_sums=True),
        'pini3hps': ft.partial(pini3, mat_gen=mat_prod_hps, tmp_sums=True),
        #'pini3hpe': ft.partial(pini3, mat_gen=mat_prod_hpe, tmp_sums=True),
        'pini3hpt': ft.partial(pini3, mat_gen=mat_prod_hp, tmp_sums=False),
        'pini2': ft.partial(pini2, mat_gen=mat_prod_0, tmp_sums=True),
        'pini2h': ft.partial(pini2, mat_gen=mat_prod_h, tmp_sums=True),
        'pini2hp': ft.partial(pini2, mat_gen=mat_prod_hp, tmp_sums=True),
        'pini2hs': ft.partial(pini2, mat_gen=mat_prod_hs, tmp_sums=True),
        'pini2hps': ft.partial(pini2, mat_gen=mat_prod_hps, tmp_sums=True),
        }

import sys

def gen_random_input(d, domain=(0,1)):
    return [random.choice(domain) for i in range(d)]

def gen_random_inputs(d, domain=(0,1)):
    x = gen_random_input(d)
    y = gen_random_input(d)
    res = {f'x_{i}': v for i, v in enumerate(x)}
    res.update({f'y_{i}': v for i, v in enumerate(y)})
    return res, x, y

def assert_sh_prod(x, y, z):
    assert (sum(x) % 2) * (sum(y) % 2) == (sum(z) % 2)

def test_mul(d, mul):
    c = mul(d)
    g = circuit_model.CompGraph(c)
    inputs, x, y = gen_random_inputs(d)
    res, _ = g.compute(inputs)
    z = [v for var, v in res.items() if c.vars[var].name.startswith('z_')]
    assert_sh_prod(x, y, z)

if __name__ == '__main__':
    try:
        d = int(sys.argv[1])
    except IndexError:
        d = 3
    for mul_name, mul_f in muls.items():
    #for mul_name, mul_f in []:
        print(f'---- {mul_name}, d={d} ----')
        print(mul_f(d))
        for _ in range(100):
            test_mul(d, mul_f)

