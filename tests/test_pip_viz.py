
from typing import Set
from unittest.mock import MagicMock

from pip_viz.pip_viz import Package, PipViz


class TestPackage:

    def test_hash(self):
        requirement = Package('Foo-Bar')
        assert hash(requirement) == hash('foo_bar')

    def test_usage_in_set(self):
        # 2 requirements with matching hashes
        requirement1 = Package('Foo-Bar')
        requirement2 = Package('foo_bar')

        requirements: Set[Package] = set()
        requirements.add(requirement1)

        assert requirement1 in requirements
        assert requirement2 in requirements
        assert 'foo_bar' not in requirements

    def test_eq(self):
        requirement1 = Package('Foo-Bar')
        requirement2 = Package('foo_bar')
        requirement3 = Package('yadayada')
        assert requirement1 == requirement2
        assert requirement1 != requirement3

    def test_get_all_dependencies(self):
        pkg1 = Package('I')

        pkg2 = Package('I.A')
        pkg3 = Package('I.B')
        pkg1.dependencies.update({
            pkg2.compare_value: pkg2,
            pkg3.compare_value: pkg3,
        })

        pkg4 = Package('I.A.1')
        pkg2.dependencies[pkg4.compare_value] = pkg4
        assert pkg1.get_all_dependencies() == {pkg2, pkg3, pkg4}


class TestPipViz:

    def test_get_packages(self):
        pip_viz = PipViz()
        pip_viz.pip_list = MagicMock(
            return_value=[
                {},
                {'name': 'foo', 'version': '1.2.3'}
            ]
        )
        dependencies = ['alpha', 'bravo']
        pip_viz.get_requirements = MagicMock(
            return_value=(
                'Foo',
                dependencies,
            )
        )
        packages = pip_viz.get_packages()

        assert isinstance(packages, dict)
        assert 1 == len(packages)
        assert {'foo'} == packages.keys()

        package = packages['foo']
        assert isinstance(package, Package)
        assert package.name == 'Foo'
        assert package.compare_value == 'foo'
        assert package.version == '1.2.3'
        assert package == Package('Foo', '1.2.3')
        assert package.dependencies == {d: Package(d) for d in dependencies}

    def test_get_requirements(self):
        pip_viz = PipViz()
        pip_viz.run_pip_show = MagicMock(
            return_value=[
                'Name: pytest',
                'Version: 8.3.3',
                'Summary: pytest: simple powerful testing with Python',
                'Home-page: None',
                'Author: Holger Krekel, Bruno Oliveira, Ronny Pfannschmidt, Floris Bruynooghe, Brianna Laugher, Florian Bruhin, Others (See AUTHORS)',
                'Author-email: None',
                'License: MIT',
                'Location: /home/john/Projects/pip-viz-venv/lib/python3.8/site-packages',
                'Requires: packaging, pluggy, iniconfig, exceptiongroup, tomli',
                'Required-by:',
            ]
        )
        name, requirements = pip_viz.get_requirements('pytest')
        assert name == 'pytest'

        expected_requirements = ['packaging', 'pluggy', 'iniconfig', 'exceptiongroup', 'tomli']
        assert requirements == expected_requirements

    def test_ignore_pip_viz_and_empty_venv_packages(self):
        pkg1 = Package('pip')
        pkg2 = Package('pkg-resources')

        pkg3 = Package('pip-viz')
        pkg4 = Package('graphviz')
        pkg3.dependencies[pkg4.compare_value] = pkg4

        pkg5 = Package('requests')

        packages = {}
        for pkg in (pkg1, pkg2, pkg3, pkg4, pkg5):
            packages[pkg.compare_value] = pkg

        packages = PipViz.ignore_pip_viz_and_empty_venv_packages(packages)
        assert packages == {pkg5.compare_value: pkg5}

    def test_ignore_pip_viz_and_empty_venv_packages__graphviz_used_elsewhere(self):
        pkg_pip = Package('pip')
        pkg_pkg_resources = Package('pkg-resources')

        pkg_pip_viz = Package('pip-viz')
        pkg_graphviz = Package('graphviz')
        pkg_pip_viz.dependencies[pkg_graphviz.compare_value] = pkg_graphviz

        pkg_requests = Package('requests')

        pkg_diagrams = Package('diagrams')
        pkg_diagrams.dependencies[pkg_graphviz.compare_value] = pkg_graphviz

        packages = {}
        for pkg in (
                pkg_pip, pkg_pkg_resources, pkg_pip_viz,
                pkg_graphviz, pkg_requests, pkg_diagrams,
        ):
            packages[pkg.compare_value] = pkg

        packages = PipViz.ignore_pip_viz_and_empty_venv_packages(packages)
        expected = {
            pkg_requests.compare_value: pkg_requests,
            pkg_diagrams.compare_value: pkg_diagrams,
            pkg_graphviz.compare_value: pkg_graphviz,
        }
        assert packages == expected
