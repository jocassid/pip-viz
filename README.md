
# pip-viz

A script that generates an svg image the dependencies within a pip virtual 
environment.  `pip-viz` uses `graphviz` Python library to generate a `.gv` 
file written in [Graphviz](https://graphviz.org)'s DOT language which is then
fed into one of Graphviz's layout engines to render the diagram.

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
