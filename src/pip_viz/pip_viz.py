#!/usr/bin/env python3

from argparse import ArgumentParser
from json import loads
from logging import basicConfig, DEBUG, getLogger
from subprocess import run
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

    def get_all_dependencies(self):
        dependencies = set()
        for dependency in self.dependencies.values():
            dependencies.add(dependency)
            dependencies.update(dependency.get_all_dependencies())
        return dependencies

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

    def __repr__(self):
        return f"{self.__class__.__name__}('{self.name}')"


class PipViz:

    def run(self, args):
        logger.info("pip-viz start")
        logger.debug(f"{args=}")
        packages: Dict[str, Package] = self.get_packages()
        if not args.all:
            self.ignore_pip_viz_and_empty_venv_packages(packages)
        self.render(packages, args.filename_root)

    @staticmethod
    def pip_list() -> List[dict]:
        args = ['pip', 'list', '--format', 'json']
        logger.debug(f"{args}")
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
        logger.debug(f"{args}")
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

    @staticmethod
    def ignore_pip_viz_and_empty_venv_packages(packages: Dict[str, Package]):
        logger.info(
            f"ignoring empty venv packages and pip-viz and it's dependencies"
        )
        empty_venv_packages = {
            'pip',
            Package.get_compare_value('pkg-resources'),
            'setuptools',
        }

        pip_viz_and_dependencies = set()
        pip_viz_package = packages.get(
            Package.get_compare_value('pip-viz'),
        )
        if pip_viz_package:
            pip_viz_and_dependencies.add(pip_viz_package.compare_value)

            all_dependencies = {
                p.compare_value for p in pip_viz_package.get_all_dependencies()
            }
            pip_viz_and_dependencies |= all_dependencies

        ignored_packages = empty_venv_packages | pip_viz_and_dependencies
        logger.info(f"{ignored_packages=}")

        # package in ignore packages will be ignored unless it's a
        # dependency of something else.
        for package in packages.values():
            compare_name = package.compare_value
            if compare_name in ignored_packages:
                continue

            depends_on_ignored = ignored_packages & package.dependencies.keys()
            if depends_on_ignored:
                ignored_packages -= depends_on_ignored

        for ignored_packages in ignored_packages:
            packages.pop(ignored_packages, None)

        return packages

    @staticmethod
    def render(packages: Dict[str, Package], filename_root: str):
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
        '-a', '--all',
        action='store_true',
        help="by default pip-viz and it's dependencies as well as: pip, "
             "pkg-resources, and setuptools are omitted from the diagram "
             "unless those packages are required by something else in the "
             "environment  To include these packages use this flag."
    )
    parser.add_argument(
        'filename_root',
        metavar='FILENAME_ROOT',
        help="This script will generate 2 files: FILENAME_ROOT.gv AND FILENAME_ROOT.gv.svg"
    )

    pip_viz = PipViz()
    pip_viz.run(parser.parse_args())


if __name__ == '__main__':
    main()
