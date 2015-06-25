Language Reference
==================

Ashes includes full support for the Dust language, and includes many
built-in functions for your convenience.

Helpers
-------

Helpers are Dust's way of providing extensibility in logic and flow
control. This may sound complex, but most Helpers are intuitive and
live up to the name. The following Helpers are provided in Ashes:

  * first
  * last
  * sep
  * idx
  * idx_1
  * size
  * iterate

Filters
-------

Filters are used to escape or otherwise process values at template
rendering time. While simple, correct Filter usage is critical. Here
are a few examples:

  * Producing readable content - ``pp`` pretty-prints values
  * Browser compliance - ``u`` escapes a URL, making it a valid href target
  * Site and user security - ``h`` escapes special characters (such as
    ``<`` and ``>``) into HTML entities (such as ``&lt;`` and
    ``&rt;``), preventing XSS and other user agent attacks

Note that if no filter is explicitly specified, Ashes errs on the safe
side and ``h`` is assumed.

Pragmas
-------

A lesser-used feature of the Dust language, Pragmas allow for
preprocessing of blocks, presumably for runtime performance
benefits. Currently there is only one built-in pragma, ``esc``, mostly
used to escape HTML code blocks and the like.
