from argparse import ArgumentParser
from .plugin import PLUGIN_MANAGER
import os
import yaml


def load_overrides():
    res = {}
    paths = [ os.path.expanduser('~/.focker.conf'), '/usr/local/etc/focker.conf',
        '/etc/focker.conf' ]
    for p in paths:
        if not os.path.exists(p):
            continue
        with open(p) as f:
            res = yaml.safe_load(f)
        break
    for k, v in os.environ.items():
        if not k.startswith('FOCKER_'):
            continue
        k = k.lower().split('_')[1:]
        r = res
        for p in k[:-1]:
            if not p in r:
                r[p] = {}
            r = r[p]
        r[k[-1]] = v
    return res


def materialize_parsers(defs, subp, overrides):
    for k, v in defs.items():
        o = overrides.get(k, {})
        parser = subp.add_parser(k, aliases=v.get('aliases', []))
        if ('subparsers' in v) + ('func' in v) != 1:
            raise KeyError('Exactly one of "subparsers" or "func" must be specified')
        if 'subparsers' in v:
            materialize_parsers(v['subparsers'], parser.add_subparsers(), o)
        elif 'func' in v:
            parser.set_defaults(func=v['func'])
            for k_1, v_1 in v.items():
                if k_1 in ['func', 'aliases']:
                    continue
                v_2 = { k: v for k, v in v_1.items() if k not in [ 'aliases' ]}
                if k_1 in o:
                    v_2['default'] = o[k_1].split(',') \
                        if ',' in o[k_1] else o[k_1]
                parser.add_argument(f'--{k_1.replace("_", "-")}',
                    *[ f'-{a}' for a in v_1.get('aliases', []) ],
                    **v_2)


def create_parser():
    parser = ArgumentParser('focker')
    subp = parser.add_subparsers()
    overrides = load_overrides()
    for p in PLUGIN_MANAGER.discovered_plugins:
        for m in p.provide_command_modules():
            materialize_parsers(m.provide_parsers(), subp, overrides)
    return parser
