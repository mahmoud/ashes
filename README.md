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
