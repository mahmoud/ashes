dust.py
=======

[Dust](http://akdubya.github.com/dustjs/) templating for Python, originally
forked from [dust-py](http://code.google.com/p/dust-py/).

A quick example:

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
