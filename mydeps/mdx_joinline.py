# -*- encoding: utf-8 -*-
"""
Join Line Extension
===================

合并段落（P）标签内的内容

主要解决VIM排版后中文内容不连续的问题

Usage:

    >>> import markdown
    >>> print markdown.markdown('line 1\\nline 2', extensions=['joinline'])
    <p>line 1 line 2</p>

Note: 这个插件和nl2br冲突。

Dependencies:
* [Python 2.4+](http://python.org)
* [Markdown 2.1+](http://packages.python.org/Markdown/)

"""

import re
from markdown.extensions import Extension
from markdown.inlinepatterns import SimpleTextPattern

CR_RE = r'(\n\s*)'


class MyPattern(SimpleTextPattern):

    def handleMatch(self, m):
        text = m.group(2)
        # 标点符号之后、单词数字之间增加一个空格
        if re.search(r'[.,;:?!]$', m.group(1)) or \
                re.search(r'(\w+|[.,;:?!])$', m.group(1)) and \
                re.match(r'\w+', m.group(3)):
            return ' '
        return ''


class JoinLineExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        cr_tag = MyPattern(CR_RE)
        md.inlinePatterns.add('joinline', cr_tag, '_end')


def makeExtension(configs=None):
    return JoinLineExtension(configs)
