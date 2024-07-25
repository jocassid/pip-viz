#!/usr/bin/env python3

from argparse import ArgumentParser
from json import loads
from subprocess import run
from sys import stderr
from typing import List

from graphviz import Digraph


def get_requires(package_name: str) -> List[str]:
    pip_show_process = run(
        ['pip', 'show', package_name],
        capture_output=True,
        text=True,
    )

    for line in pip_show_process.stdout.split('\n'):
        pieces = line.split(': ')
        if len(pieces) != 2:
            continue
        if pieces[0] != 'Requires':
            continue
        requirements = pieces[1]
        if not requirements:
            break
        return requirements.split(', ')

    return []


def main(args):
    pip_list_process = run(
        ['pip', 'list', '--format', 'json'],
        capture_output=True,
        text=True,
    )

    graph = Digraph(
        args.filename_root,
        format='svg',
        node_attr={'shape': 'rectangle'},
        graph_attr={'rankdir': 'LR'}
    )

    for dependency in loads(pip_list_process.stdout):
        name = dependency.get('name') or ''
        if not name:
            print(f"No name found in {dependency}", stderr)
            continue

        print(f"Processing {name}")
        graph.node(name)

        requires = get_requires(name)
        if not requires:
            continue

        for requirement in requires:
            graph.edge(name, requirement)

    graph.render()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        'filename_root',
        metavar='FILENAME_ROOT',
        help="This script will generate 2 files: FILENAME_ROOT.gv AND FILENAME_ROOT.gv.svg"
    )
    main(parser.parse_args())
