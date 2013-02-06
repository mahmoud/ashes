Ashes
=====

[Dust](http://akdubya.github.com/dustjs/) templating for Python.

A quick example (which will work again soon):

```python
>>> from ashes import ashes
>>> ashes.compile("Hello, {name}!", 'hello')
>>> ashes.render('hello', {'name': 'World'})
'Hello, World!'
>>> ashes.load('hella.html', 'hella')
>>> ashes.render('hella', {'names': ['Kurt', 'Alex']})
'Hella Kurt and Alex!'
```

For more info, see the [Dust documentation](http://akdubya.github.com/dustjs/).

## Installation

Ashes is implemented as a single .py file, so installation can be as
easy as downloading `ashes.py` above and putting it in the same
directory as your project. And of course you can always `pip install ashes`.


## Compatibility

Ashes has full support for every feature of the original Dust.js. Here's
a what the test suite says about all of the examples on Dust's documentation:

```
  . = passed, _ = skipped, X = failed, E = exception

 Dust.js site refs   tokenize   parse    optimize  compile    render
---------------------------------------------------------------------
                path    .         .         _         .         .
               plain    .         .         _         .         .
                zero    .         .         _         .         .
           async_key    .         .         _         .         .
          sync_chunk    .         .         _         .         .
            sync_key    .         .         _         .         .
              params    .         .         _         .         .
     partial_context    .         .         _         .         .
             escaped    .         .         _         .         .
            implicit    .         .         _         .         .
              filter    .         .         _         .         .
         empty_array    .         .         _         .         .
               array    .         .         _         .         .
            partials    .         .         _         .         .
               intro    .         .         _         .         E
           recursion    .         .         _         .         .
              object    .         .         _         .         .
       force_current    .         .         _         .         .
             replace    .         .         _         .         .
          rename_key    .         .         _         .         .
             context    .         .         _         .         .
      async_iterator    .         .         _         .         .
  interpolated_param    .         .         _         .         .
            comments    .         _         _         .         .
       escape_pragma    .         .         .         .         .
       base_template    .         .         _         .         .
          else_block    .         .         _         .         .
      child_template    .         .         _         .         .
         conditional    .         .         .         .         .
---------------------------------------------------------------------
          (29 total)    29        28        2         29        28
```

(NOTE: Optimization is fairly straightforward, so only two of the more
complex examples are tested.)

### A word on functions

Of course, being a Python library, functions and callable items in the
contexts intended for server-side rendering must be written in
Python. However, there are three reasons this is desirable:

   1. Many context functions control some element of UI, such as
   a transition or delay, which would just waste cycles if executed
   server-side. (e.g., 'Intro' on the dust.js docs above)
   2. One-off context functions should be extremely basic, or
   3. Common, complex functions should be refactored into Helpers
   and registered in the rendering environment for all templates
   to use.

At the end of the day, though, remember that Dust is meant to be
data-driven, and if one finds oneself with highly complex functions in
the rendering contexts, one would do well to explore other templating
solutions.

### Other notes on compatibility

* Comments are parsed differently, but both Ashes and Dust simply
  strip them out.

Ashes has been tested on Python 2.7.
