Ashes
=====

[![Build Status](https://travis-ci.org/mahmoud/ashes.png?branch=master)](https://travis-ci.org/mahmoud/ashes)

[Dust](http://akdubya.github.com/dustjs/) templating for Python 2 and 3.
Also the most convenient, portable, and powerful [command-line
templating utility](#command-line-interface).

A quick example:

```python
>>> from ashes import AshesEnv
>>> ashes_env = AshesEnv()

# Register/render from source

>>> ashes_env.register_source('hello', 'Hello, {name}!')
>>> ashes_env.render('hello', {'name': 'World'})
'Hello, World!'

# Or a file-based template (note: hella templates sold separately)

>>> ashes_env2 = AshesEnv(['./templates'])
>>> ashes_env2.render('hella.html', {'names': ['Kurt', 'Alex']})
'Hella Kurt and Alex!'
```

There's also built-in [bottle.py](http://bottlepy.org/docs/dev/)
support, which works exactly like bottle's own `template()` function
and `view()` decorator.

```python
from ashes import ashes_bottle_template as template
from ashes import ashes_bottle_view as view

@route('/')
def hello(name='World'):
    return template('bottle_hello_template', name=name)

@route('/dec')
@view('bottle_hello_template')
def hello_dec(name='World'):
    return {'name': name}

# Use debug=True to disable template caching for easier dev
run(host='localhost', port=8080, reloader=True, debug=True)
```

If you've read [bottle's template
docs](http://bottlepy.org/docs/dev/tutorial.html#templates), it'll be
even dead-simpler, believe it or not.

One last tip, use the `keep_whitespace` flag to determine whether or
not to optimize away whitespace in the rendered template. It's a good
idea to keep this disabled if you use JavaScript in your templated
files, because occasionally a single-line comment (i.e., `// ...` can
break your page.

```python
ashes_env = AshesEnv(keep_whitespace=False)  # optimize away whitespace
```

For more general information about the dust templating language, see
the [Dust documentation](http://akdubya.github.com/dustjs/).


# Command-line interface

The ashes command-line interface serves two purposes. First, it makes
it easy to experiment with and test ashes features and behavior,
especially thanks to the inline "literal" options, demonstrated
below.

```sh
# using ashes to pretty-print JSON
$ python ashes.py --no-filter -T '{.|ppjson}' -M '{"x": {"y": [1,2,3]}}'
{
  "x": {
      "y": [
        1,
        2,
        3,
      ]
   }
}
```

Secondly, thanks to the compact, single-file implementation,
ashes can replace rusty sed and awk scripts, wherever Python 2.7-3.x
is available. Use ashes for generating shell scripts and much more.

Templates can be files or passed at the command line. Models, the
input data to the template, are passed in as JSON, either as a command
line option, or through stdin, enabling piping from web
requests. Several other options exist, see the help output below.

```
$ python ashes.py --help
Usage: ashes.py [options]

render a template using a JSON input

Options:
  --version             show program's version number and exit
  -h, --help            show this help message and exit
  --env-path=ENV_PATH   paths to search for templates, separate paths with :
  --filter=FILTER       autoescape values with this filter, defaults to 'h'
                        for HTML
  --no-filter           disables default HTML-escaping filter, overrides
                        --filter
  --trim-whitespace     removes whitespace on template load
  -m MODEL_PATH, --model=MODEL_PATH
                        path to the JSON model file, default - for stdin
  -M MODEL_LITERAL, --model-literal=MODEL_LITERAL
                        the literal string of the JSON model, overrides model
  -o OUTPUT_PATH, --output=OUTPUT_PATH
                        path to the output file, default - for stdout
  --output-encoding=OUTPUT_ENCODING
                        encoding for the output, default utf-8
  -t TEMPLATE_PATH, --template=TEMPLATE_PATH
                        path of template to render, absolute or relative to
                        env-path
  -T TEMPLATE_LITERAL, --template-literal=TEMPLATE_LITERAL
                        the literal string of the template, overrides template
  --verbose=VERBOSE     emit extra output on stderr
```


## Installation

Ashes is implemented as a single .py file, so installation can be as
easy as downloading `ashes.py` above and putting it in the same
directory as your project. And of course you can always `pip install ashes`.

## Testimonials

Ashes is currently used in production settings at PayPal and Rackspace.

Additionally, it is part of
[the Clastic web framework](https://github.com/mahmoud/clastic) and
used [in several Wikimedia-oriented projects](https://github.com/hatnote).

If your company or project uses Ashes, feel free to submit an issue or
pull request to get a link or shoutout added to this section.

## Compatibility

Ashes has full support for every feature of the original Dust.js. Here's
what the test suite says about all of the examples on Dust's documentation:

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
               intro    .         .         _         .         .
           recursion    .         .         _         .         .
              object    .         .         _         .         .
       force_current    .         .         _         .         .
             replace    .         .         _         .         .
          rename_key    .         .         _         .         .
             context    .         .         _         .         .
      async_iterator    .         .         _         .         .
  interpolated_param    .         .         _         .         .
            comments    .         .         _         .         .
       escape_pragma    .         .         .         .         .
       base_template    .         .         _         .         .
          else_block    .         .         _         .         .
      child_template    .         .         _         .         .
         conditional    .         .         .         .         .
---------------------------------------------------------------------
          (29 total)    29        29        2         29        29

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

* Ashes uses a different parsing mechanism than dust, so on a few
rare corner cases, like comments placed within string literals, the
template behavior might differ.

Ashes has been tested extensively on Python 2.7, as well as 2.6, 3.2,
3.3, and PyPy.


## Things to watch out for

* Accidentally passing functions in as values to a
  template. Dust/Ashes calls all functions referenced by the
  template. If the function isn't of the right signature, you may see
  a TypeError.

* Leaving optimization enabled, especially when JavaScript is embedded
  in the page. Dust-style optimization is meant for HTML/XML and is
  nowhere near as smart as JavaScript/CSS minification suites. For
  example, a mixed-mode page (HTML/JS/CSS all in one page) may appear
  to work fine until the addition of a '//' single-line comment. When
  Dust/Ashes turns this into a single line, the page from that point
  on is treated as one long comment.
