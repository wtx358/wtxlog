# -*- encoding: utf-8 -*-
import os
import sys
if sys.platform == 'win32':
    pybabel = 'pybabel'
else:
    pybabel = 'pybabel'
os.system(pybabel + ' compile -d ../translations')
