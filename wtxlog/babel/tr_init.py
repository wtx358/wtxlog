# -*- encoding: utf-8 -*-
import os
import sys
if sys.platform == 'win32':
    pybabel = 'pybabel'
else:
    pybabel = 'pybabel'
if len(sys.argv) != 2:
    print("usage: tr_init <language-code>")
    sys.exit(1)
os.system(pybabel + ' extract -F babel.ini -k lazy_gettext --project wtxlog -o messages.pot ..')
os.system(pybabel + ' init -i messages.pot -d ../translations -l ' + sys.argv[1])
os.unlink('messages.pot')
