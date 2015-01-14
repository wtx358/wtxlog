# -*- encoding: utf-8 -*-
import os
import sys
if sys.platform == 'win32':
    pybabel = 'pybabel'
else:
    pybabel = 'pybabel'
os.system(pybabel + ' extract -F babel.ini -k lazy_gettext --project wtxlog -o messages.pot ..')
os.system(pybabel + ' update -i messages.pot -d ../translations')
os.unlink('messages.pot')
