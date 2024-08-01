#!/usr/bin/env python3

from argparse import ArgumentParser
from json import loads
from subprocess import run
from sys import stderr
from typing import List, Set

from graphviz import Digraph


def get_requirements(package_name: str) -> List[str]:
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


def add_node_to_graph(
        node_name: str,
        node_label: str,
        node_set: Set[str],
        graph: Digraph,
):
    if node_name in node_set:
        return
    graph.node(node_name, node_label)
    node_set.add(node_name)


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
        graph_attr={
            'rankdir': 'LR',
            'splines': "ortho",
            'mclimit': '4.0',
            'ranksep': '1.0',
        }
    )

    node_names: Set[str] = set()

    for package_dict in loads(pip_list_process.stdout):
        package: str = package_dict.get('name') or ''
        if not package:
            print(f"No name found in {package_dict}", stderr)
            continue

        print(f"Processing {package}")

        package_node: str = package.lower()
        add_node_to_graph(package_node, package, node_names, graph)

        for requirement in get_requirements(package):
            requirement_node = requirement.lower()
            add_node_to_graph(requirement_node, requirement, node_names, graph)
            graph.edge(package_node, requirement_node)

    graph.render()


def parse_args_and_call_main():
    parser = ArgumentParser()
    parser.add_argument(
        'filename_root',
        metavar='FILENAME_ROOT',
        help="This script will generate 2 files: FILENAME_ROOT.gv AND FILENAME_ROOT.gv.svg"
    )
    main(parser.parse_args())


if __name__ == '__main__':
    parse_args_and_call_main()
