#!/usr/bin/env python3

from argparse import ArgumentParser
from json import loads
from logging import basicConfig, DEBUG, getLogger
from subprocess import run
from sys import stderr
from typing import Dict, List, Tuple

from graphviz import Digraph


logger = getLogger(__name__)


class Package:
    def __init__(self, name: str, version: str = ''):
        self._name = name
        self.compare_value = Package.get_compare_value(name)
        self.version = version
        self.dependencies: Dict[str, Package] = {}

    @staticmethod
    def get_compare_value(name):
        return name.replace('-', '_').lower()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name
        self.compare_value = self.get_compare_value(name)

    def __hash__(self):
        return hash(self.compare_value)

    def __eq__(self, other):
        if not isinstance(other, Package):
            return False
        if self.compare_value != other.compare_value:
            return False
        if self.version != other.version:
            return False
        return True


class PipViz:

    def run(self, args):
        logger.info("pip-viz start")
        packages: Dict[str, Package] = self.get_packages()
        self.render(packages, args.filename_root)

    @staticmethod
    def pip_list() -> List[dict]:
        args = ['pip', 'list', '--format', 'json']
        logger.debug(f"{args=}")
        pip_list_process = run(
            args,
            capture_output=True,
            text=True,
        )
        json = loads(pip_list_process.stdout)
        return json

    def get_packages(self) -> Dict[str, Package]:
        packages: Dict[str, Package] = {}
        for i, package_dict in enumerate(self.pip_list()):
            if i > 0 and i % 5 == 0:
                print(f"{i} packages processed")

            package = Package(
                package_dict.get('name') or '',
                package_dict.get('version') or '',
            )
            if not package.name:
                logger.error(f"No name found in {package_dict}")
                continue
            if not package.version:
                logger.error(f"No version found for package {package.name}")
                continue

            key = package.compare_value
            package = packages.get(key) or package
            packages[key] = package

            name, dependencies = self.get_requirements(package.name)
            package.name = name  # In case name in pip show differs (case, hyphen vs. underscore)
            for dependency in dependencies:
                dependency = Package(dependency)
                dependency = packages.get(dependency.compare_value) or dependency
                package.dependencies[dependency.compare_value] = dependency
        return packages

    @staticmethod
    def run_pip_show(package_name: str):
        args = ['pip', 'show', package_name]
        logger.debug(f"{args=}")
        pip_show_process = run(
            args,
            capture_output=True,
            text=True,
        )
        return pip_show_process.stdout.split('\n')

    def get_requirements(self, package_name: str) -> Tuple[str, List[str]]:
        name = ''
        requirements = []

        for i, line in enumerate(self.run_pip_show(package_name)):
            label, *rest = line.split(': ')
            if len(rest) != 1:
                continue
            rest = rest[0]

            if i == 0 and label == 'Name':
                name = rest.strip()
                continue

            if label == 'Requires':
                if rest:
                    requirements = rest.split(', ')
                break

        return name, requirements

    def render(self, packages: Dict[str, Package], filename_root: str):
        graph = Digraph(
            filename_root,
            format='svg',
            node_attr={'shape': 'rectangle'},
            graph_attr={
                'rankdir': 'LR',
                'splines': "ortho",
                'mclimit': '4.0',
                'ranksep': '1.0',
            }
        )

        for package in packages.values():
            graph.node(
                package.compare_value,
                f"{package.name} {package.version}",
            )

        for package in packages.values():
            for dependency in package.dependencies.values():
                graph.edge(
                    package.compare_value,
                    dependency.compare_value,
                )

        graph.render()


def main():
    basicConfig(
        format=" %(levelname)s:%(asctime)s:%(filename)s:%(lineno)d:%(message)s",
        filename='pip_viz.log',
        level=DEBUG
    )

    parser = ArgumentParser()
    parser.add_argument(
        'filename_root',
        metavar='FILENAME_ROOT',
        help="This script will generate 2 files: FILENAME_ROOT.gv AND FILENAME_ROOT.gv.svg"
    )

    pip_viz = PipViz()
    pip_viz.run(parser.parse_args())


if __name__ == '__main__':
    main()
