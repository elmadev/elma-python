import sys
import os

sys.path.insert(0, os.path.abspath('..'))
extensions = ['sphinx.ext.autodoc', 'sphinxcontrib.napoleon']
source_suffix = '.rst'
master_doc = 'index'
project = u'Elma Python Library'
copyright = u'2015, Elma Library Contributors'
exclude_patterns = ['_build']
pygments_style = 'sphinx'
todo_include_todos = False
html_theme = 'sphinx_rtd_theme'
