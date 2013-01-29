INTRO = r'''{#stream}{#delay}{.}{/delay}{/stream}'''
PLAIN = r'''Hello World!'''
REPLACE = r'''Hello {name}! You have {count} new messages.'''
ZERO = r'''{#zero}{.}{/zero}'''
ARRAY = r'''{#names}{title} {name}{~n}{/names}'''
EMPTY_ARRAY = r'''{#names}{title} {name}{~n}{/names}'''
IMPLICIT = r'''{#names}{.}{~n}{/names}'''
OBJECT = r'''{#person}{root}: {name}, {age}{/person}'''
RENAME_KEY = r'''{#person foo=root}{foo}: {name}, {age}{/person}'''
FORCE_CURRENT = r'''{#person}{.root}: {name}, {age}{/person}'''
PATH = r'''{foo.bar}'''
ESCAPED = r'''{safe|s}{~n}{unsafe}'''
ESCAPE_PRAGMA = r'''{safe|s}{~n}{unsafe}'''

ELSE_BLOCK = \
r'''{#foo}
  foo,{~s}
{:else}
  not foo,{~s}
{/foo}
{#bar}
  bar!
{:else}
  not bar!
{/bar}'''

CONDITIONAL = \
r'''{?tags}
  <ul>{~n}
    {#tags}
      {~s} <li>{.}</li>{~n}
    {/tags}
  </ul>
{:else}
  No Tags!
{/tags}
{~n}
{^likes}
  No Likes!
{:else}
  <ul>{~n}
    {#likes}
      {~s} <li>{.}</li>{~n}
    {/likes}
  </ul>
{/likes}'''

SYNC_KEY = r'''Hello {type} World!'''
ASYNC_KEY = r'''Hello {type} World!'''
SYNC_CHUNK = r'''Hello {type} World!'''
ASYNC_ITERATOR = r'''{#numbers}{#delay}{.}{/delay}{@sep}, {/sep}{/numbers}'''
FILTER = r'''{#filter}foo {bar}{/filter}'''
CONTEXT = r'''{#list:projects}{name}{:else}No Projects!{/list}'''
PARAMS = r'''{#helper foo="bar"/}'''
PARTIALS = r'''{>replace/} {>"plain"/} {>"{ref}"/}'''
PARTIAL_CONTEXT = r'''{>replace:.profile/}'''

BASE_TEMPLATE = \
r'''Start{~n}
{+title}
  Base Title
{/title}
{~n}
{+main}
  Base Content
{/main}
{~n}
End'''

CHILD_TEMPLATE = \
r'''{^xhr}
  {>base_template/}
{:else}
  {+main/}
{/xhr}
{<title}
  Child Title
{/title}
{<main}
  Child Content
{/main}'''

RECURSION = r'''{name}{~n}{#kids}{>recursion:./}{/kids}'''

COMMENTS = \
r'''{!
  Multiline
  {#foo}{bar}{/foo}
!}
{!before!}Hello{!after!}'''


ref_templates = {}
for name, tmpl_source in globals().items():
    if not name.isupper() or name.startswith('_'):
        continue
    ref_templates[name.lower()] = tmpl_source


if __name__ == '__main__':
    print 'known templates:', ref_templates.keys()
