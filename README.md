
# pip-viz

A script that generates an SVG image displaying the dependencies within a pip 
virtual environment.

## Installation

`pip-viz` uses `graphviz` Python library to generate 
a `.gv` file containing instructions written in [Graphviz](https://graphviz.org)'s
DOT language.  The Graphviz application takes the instructions written in the
`.gv` file and generates an image.  

The [Graphviz](https://graphviz.org) application will need to be installed
separately.  Linux, Windows, and Mac versions are available and the graphviz
executable `dot` will need to be on your `PATH`.

With your virtualenv active, install from the Python Package Index (PyPI) 
with the following command:

`pip install pip-viz`

Once installed, use the `pip-viz` executable to render a diagram for the 
current virtualenv.  The syntax for this command is:

`pip-viz my_app_dependencies`

This command will generate two files in the current working directory:

- `my_app_dependencies.gv` - The file that defines the graph in the DOT language
- `my_app_dependencies.gv.svg` - An SVG image that you can view in your web 
browser.  You can use the zoom, scroll, and find features of your browser to 
navigate the diagram.

By default, pip-viz and it's dependencies as well as packages that are present
in a newly created virtualenv will be ignored unless:
1. The package is a dependency of a package which is not ignored
2. The `-a` (or `--all`) command line flag is used.

## Changelog

### 0.0.7

- Ignoring pip-viz and its dependencies as well as packages that are present
  in a newly created virtualenv 

### 0.0.6

- fixed project.scripts so package can be run using 'pip-viz'

### 0.0.5

- Refactored, added version numbers for packages.
- Added logging
- Created some tests

### 0.0.4

- Made this package pip installable

### 0.0.3

- Added graph attributes to make graph easier to read

### 0.0.2

- Fixed problem with duplicate notes

### 0.0.1

- Initial version