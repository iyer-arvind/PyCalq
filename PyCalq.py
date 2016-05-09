#!/usr/bin/env python

from collections import OrderedDict
import re
import sys

import numpy as np
from pint import UnitRegistry
from scipy.optimize import fmin

ureg = UnitRegistry()

lcls = {'pi': np.pi, 'sqrt': np.sqrt, 'pow': np.power,
        '_U': ureg}

np.seterr(all='ignore')


def parse_input(file_name):
    with open(sys.argv[1], 'r') as fh:
        eqns = []
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
                I = line.index('=')
                eqns.append(('('+line[:I]+')', '('+line[I+1:]+')'))

            elif STATE == 'G':
                if ':=' in line:
                    var, val = line.split(':=')
                    pardict[var] = eval(val, lcls)
                    lcl.update(vardict)

                else:
                    var, val = line.split('=')
                    vardict[var] = eval(val, lcls)
                    lcl.update(vardict)

    return eqns, vardict, pardict


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


if __name__ == '__main__':
    from argparse import ArgumentParser
    parser = ArgumentParser(
        'Simultaneous NonLinear Equation Solver with Units')
    parser.add_argument('input', type=str)
    args = parser.parse_args()

    eqns, vardict, pardict = parse_input(args.input)
    vals = solve(eqns, vardict, pardict)

    print('{} equations, {} variables, {} parameters'.format(
        len(eqns), len(vardict), len(pardict)))

    from tabulate import tabulate
    print(tabulate(vals.items()))
