from __future__ import unicode_literals

PLAIN = r'Hello World!'
REPLACE = r'Hello Mick! You have 30 new messages.'
ZERO = r'''0'''

ARRAY = \
r'''Sir Moe
Sir Larry
Sir Curly'''

EMPTY_ARRAY = ''

IMPLICIT = \
r'''Moe
Larry
Curly'''

OBJECT = 'Subject: Larry, 45'
RENAME_KEY = OBJECT
FORCE_CURRENT = ': Larry, 45'
PATH = 'Hello!'

ESCAPED = \
r'''<script>alert('Hello!')</script>
&lt;script&gt;alert('Goodbye!')&lt;/script&gt;'''

ESCAPE_PRAGMA = \
r'''<script>alert('Goodbye!')</script>
&lt;script&gt;alert('Goodbye!')&lt;/script&gt;'''

ELSE_BLOCK = 'foo, not bar!'

CONDITIONAL = \
r'''No Tags!
<ul>
  <li>moe</li>
  <li>larry</li>
  <li>curly</li>
  <li>shemp</li>
</ul>'''

SYNC_KEY = 'Hello Sync World!'
ASYNC_KEY = 'Hello Async World!'
SYNC_CHUNK = 'Hello Chunky World!'
ASYNC_ITERATOR = '3, 2, 1'
FILTER = 'FOO BAR'

CONTEXT = \
r'''<ul>
<li>Mayhem</li>
<li>Flash</li>
<li>Thunder</li>
</ul>'''

PARAMS = 'bar'
PARTIALS = 'Hello Jim! You have 42 new messages. Hello World! Hello World!'
PARTIAL_CONTEXT = 'Hello Mick! You have 30 new messages.'

BASE_TEMPLATE = \
r'''Start
Base Title
Base Content
End'''

CHILD_TEMPLATE = \
r'''Start
Child Title
Child Content
End'''

RECURSION = \
r'''1
1.1
1.1.1'''

COMMENTS = 'Hello'

ref_renders = {}
for name, render_res in globals().items():
    if not name.isupper() or name.startswith('_'):
        continue
    ref_renders[name.lower()] = render_res


if __name__ == '__main__':
    print 'known renders:', ref_renders.keys()
