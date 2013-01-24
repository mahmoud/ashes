dust.py
=======

[Dust](http://akdubya.github.com/dustjs/) templating for Python, originally
based on [dust-py](http://code.google.com/p/dust-py/), but now in the process
of being rewritten, since dust-py was incomplete, buggy, and didn't compile
to python.

A quick example (which will work again soon):

```python
>>> from dust import dust
>>> dust.compile("Hello, {name}!", 'hello')
>>> dust.render('hello', {'name': 'World'})
'Hello, World!'
>>> dust.load('hella.html', 'hella')
>>> dust.render('hella', {'names': ['Kurt', 'Alex']})
'Hella Kurt and Alex!'
```

For more info, see the [Dust documentation](http://akdubya.github.com/dustjs/).
