'''
Search all of the .py files in a directory for longest functions by
number of source lines.

Usage:
  dirt.py DIRECTORY [NUM_RESULTS]

'''
from __future__ import print_function
from tabulate import tabulate
import ast
import astunparse
import fnmatch
import os


class Func(object):
    def __init__(self, node, filename):
        self.node = node
        self.lineno = node.lineno
        self.filename = filename
        self.name = node.name
        self.unparsed = astunparse.unparse(node)
        self.source = ''.join(self.unparsed).strip()
        self.linecount = len(self.source.splitlines())


def locate(pattern, root=os.curdir):
    """
    Locate all files matching supplied filename pattern in and below
    supplied root directory.
    """
    for path, dirs, files in os.walk(os.path.abspath(root)):
        for filename in fnmatch.filter(files, pattern):
            yield os.path.join(path, filename)


def extract_function_nodes(fn):
    try:
        with open(fn, 'r') as f:
            mod = ast.parse(f.read(), fn)
    except Exception:
        print('Error parsing', fn)
        return []
    return [Func(n, fn) for n in mod.body if isinstance(n, ast.FunctionDef)]


def main(directory, num_results):
    all_function_nodes = []
    file_names = list(locate('*.py', directory))
    print(len(file_names), 'files')

    for fn in file_names:
        all_function_nodes.extend(extract_function_nodes(fn))

    all_function_nodes.sort(key=lambda n: n.linecount, reverse=True)
    all_function_nodes = all_function_nodes[:num_results]

    table = [(func.linecount,
              func.name,
              '%s:%s' % (os.path.relpath(func.filename, directory),
                         func.lineno))
             for func in all_function_nodes]
    print(tabulate(table, headers=('Lines', 'Function', 'Location')))


if __name__ == "__main__":
    import docopt
    args = docopt.docopt(__doc__)
    directory = args['DIRECTORY'] or os.curdir
    num_results = args['NUM_RESULTS'] or 20
    main(directory, num_results)
