#!/usr/bin/env python

from collections import OrderedDict
import itertools as it
import re
import sys

import numpy as np
from pint import UnitRegistry
from scipy.optimize import fmin

ureg = UnitRegistry()

lcls = {'pi': np.pi, 'sqrt': np.sqrt, 'pow': np.power,
        '_U': ureg}

np.seterr(all='ignore')


def get_solution_order(var_list):
    all_vars = set(k for v in var_list for k in v)
    assert len(all_vars) <= len(var_list), 'vars: {} not same as {}'.format(all_vars, var_list)
    ev_list = list(enumerate(var_list))

    def resolve(level):
        for prm in it.permutations(ev_list, level):
            eq, vl = zip(*prm)
            vv = set(k for v in vl for k in v)
            if len(vv) == level:
                nl = [(e[0], e[1]-vv) for e in ev_list if e[0] not in eq]
                return eq, nl, vv
        return None, None, None

    sol_ord = []

    while ev_list:
        for N in range(1, len(ev_list)+1):
            eqsolve, new_list, vv = resolve(N)
            if eqsolve is not None:
                ev_list = new_list
                sol_ord.append((eqsolve, vv))
                break
        else:
            raise ValueError

    return sol_ord


def parse_input(file_name):
    with open(sys.argv[1], 'r') as fh:
        eqns = []
        var_list = []
        STATE = 'E'
        lcl = dict(lcls)
        vardict = OrderedDict()
        pardict = OrderedDict()

        for line in fh:
            line = line.strip()
            if '//' in line:
                line = line[:line.index('//')]

            if not line:
                continue
            line = re.sub(r'\[([^]]*)\]', r'*_U("\1")', line)
            if line == '::':
                STATE = 'G'
                continue

            if STATE == 'E':
                var_list.append(set(re.findall(r'[^\d\W]\w*', line)))
                I = line.index('=')
                eqns.append(('('+line[:I]+')', '('+line[I+1:]+')'))

            elif STATE == 'G':
                if ':=' in line:
                    var, val = line.split(':=')
                    pardict[var.strip()] = eval(val, lcls)
                    lcl.update(pardict)

                else:
                    var, val = line.split('=')
                    vardict[var.strip()] = eval(val, lcls)
                    lcl.update(vardict)

    for v in var_list:
        v -= set(pardict)
        v -= set(lcls)

    eqns_order = get_solution_order(var_list)

    return ([(tuple(eqns[e] for e in eo), vv) for eo, vv in eqns_order],
            vardict, pardict)


def solve(eqns, vardict, pardict):
    def errsq(testvars, *args):
        lcl = dict(lcls)
        for n, m, u in zip(var_n, testvars, var_u):
            lcl[n] = m if u.dimensionless else u * m

        lcl.update(zip(pardict.keys(), args))

        sqerr = 0
        for l, r in eqns:
            lv = eval(l, lcl)
            rv = eval(r, lcl)
            if type(lv) is ureg.Quantity or type(rv) is ureg.Quantity:
                lv = ureg.Quantity(lv)
                rv = ureg.Quantity(rv)
                assert (lv.u/rv.u).dimensionless,\
                    '"{} = {}" units dont match ({}, {})'.format(
                        l, r, lv.to_base_units().u,
                        rv.to_base_units().u)

            mv = max(abs(lv), abs(rv))
            sqerr += float(((lv - rv) / mv) ** 2)

        return sqerr

    var_u = tuple(v.u if type(v) is ureg.Quantity else ureg.Quantity(1)
                  for v in vardict.values())

    var_m = tuple(v.m if type(v) is ureg.Quantity else v
                  for v in vardict.values())

    var_n = tuple(vardict.keys())

    while True:
        var_m = fmin(errsq, var_m,
                     tuple(pardict.values()), disp=False,
                     ftol=1e-12, xtol=1e-12, maxfun=1000000, maxiter=1000000)

        err = errsq(var_m, *tuple(pardict.values()))

        if err < 1e-8:
            break

    return dict((n, m if u.dimensionless else m*u)
                for n, m, u in zip(var_n, var_m, var_u))

def main():
    from argparse import ArgumentParser
    parser = ArgumentParser(
        'Simultaneous NonLinear Equation Solver with Units')
    parser.add_argument('input', type=str)
    args = parser.parse_args()

    eqns, vardict, pardict = parse_input(args.input)
    for eq, vv in eqns:
        vals = solve(eq, {v: vardict[v] for v in vv}, pardict)
        pardict.update(vals)

    from tabulate import tabulate
    print(tabulate((v, pardict[v]) for v in vardict))


if __name__ == '__main__':
    main()
