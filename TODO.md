# TODO
 * remove unnecessary callback dynamics
 * stop using dicts to get around javascript's array behavior
   (assignments to indexes > len(x) autocreate undefined elements)
 * make a nice Template class
 * add flags for common Optimization tweaks (e.g., whitespace on/off)
 * docs, of course
 * more tests (corner cases, negative cases, larger pages)
   * what happens if tags spans multiple lines?
 * pragmas
 * benchin'
   * `__slots__`?
 * keep track of unresolved symbols and proffer a blank schema for
   introspection/convenience?
 * handle comments better
 * line/column number for errors
 * rendering support for root-level recursive templates
 * Interpolated values in parameters
 * nosetests

# Notes
 * Javascript implicitly disregards extra arguments passed
 to a function, so a lot of dust.js's functions were weird
 to port. Especially so in the case of code generation.
 Example: the exists tag takes params, but they're pushed into
 the stack/context by the time the generated code runs. Nevertheless,
 the generated js passes them to the Chunk.exists() function, even
 though it doesn't take them.
