# -*- coding: utf-8 -*-

# say hello for test

import sys
from os import path

deps_paths = [
    path.join(path.split(path.realpath(__file__))[0], 'deps'), 
    path.join(path.split(path.realpath(__file__))[0], 'mydeps'),
]

for deps_path in deps_paths:
    if deps_path not in sys.path:
        sys.path.insert(0, deps_path)

from wtxlog import create_app

app = create_app('default')

if __name__ == '__main__':
    app.run(debug=True)
