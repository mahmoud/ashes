from __future__ import unicode_literals

import json

INTRO = r'''function() {
  var d = 1;
  return {
    stream: function() {
      return "asynchronous templates for the browser and node.js".split('');
    },
    delay: function(chunk, context, bodies) {
      return chunk.map(function(chunk) {
        setTimeout(function() {
          chunk.render(bodies.block, context).end();
        }, d++ * 15);
      });
    }
  }
}'''

PLAIN = '{}'
REPLACE = r'''{
  "name": "Mick",
  "count": 30
}'''

ZERO = r'''{
  "zero": 0
}'''

ARRAY = r'''{
  "title": "Sir",
  "names": [{
    "name": "Moe"
  },
  {
    "name": "Larry"
  },
  {
    "name": "Curly"
  }]
}'''

EMPTY_ARRAY = r'''{
  "title": "Sir",
  "names": []
}'''

IMPLICIT = r'''{
  "names": ["Moe", "Larry", "Curly"]
}'''

OBJECT = r'''{
  "root": "Subject",
  "person": {
    "name": "Larry",
    "age": 45
  }
}'''

RENAME_KEY = OBJECT
FORCE_CURRENT = OBJECT

PATH = '''{
  "foo": {
    "bar": "Hello!"
  }
}'''

ESCAPED = r'''{
  "safe": "<script>alert('Hello!')</script>",
  "unsafe": "<script>alert('Goodbye!')</script>"
}'''

ESCAPE_PRAGMA = r'''{
  "unsafe": "<script>alert('Goodbye!')</script>"
}'''

ELSE_BLOCK = r'''{
  "foo": true,
  "bar": false
}'''

CONDITIONAL = r'''{
  "tags": [],
  "likes": ["moe", "larry", "curly", "shemp"]
}'''

SYNC_KEY = r'''{
  "type": function(chunk) {
    return "Sync";
  }
}'''

ASYNC_KEY = r'''{
  "type": function(chunk) {
    return chunk.map(function(chunk) {
      dust.nextTick(function() {
        chunk.end("Async");
      });
    });
  }
}'''

ASYNC_ITERATOR = r'''{
  "numbers": [
  3, 2, 1],
  "delay": function(chunk, context, bodies) {
    return chunk.map(function(chunk) {
      setTimeout(function() {
        chunk.render(bodies.block, context).end();
      }, Math.ceil(Math.random() * 10));
    });
  }
}'''

FILTER = r'''{
  "filter": function(chunk, context, bodies) {
    return chunk.tap(function(data) {
      return data.toUpperCase();
    }).render(bodies.block, context).untap();
  },
  "bar": "bar"
}'''

CONTEXT = r'''{
  "list": function(chunk, context, bodies) {
    var items = context.current(),
        len = items.length;

    if (len) {
      chunk.write("<ul>\n");
      for (var i = 0; i < len; i++) {
        chunk = chunk.write("<li>").render(bodies.block, context.push(items[i])).write("</li>\n");
      }
      return chunk.write("</ul>");
    } else if (bodies['else']) {
      return chunk.render(bodies['else'], context);
    }
    return chunk;
  },
  "projects": [{
    "name": "Mayhem"
  },
  {
    "name": "Flash"
  },
  {
    "name": "Thunder"
  }]
}'''

PARAMS = r'''{
  "helper": function(chunk, context, bodies, params) {
    return chunk.write(params.foo);
  }
}'''

PARTIALS = r'''{
  "name": "Jim",
  "count": 42,
  "ref": "plain"
}'''

PARTIAL_CONTEXT = r'''{
  "profile": {
    "name": "Mick",
    "count": 30
  }
}'''

BASE_TEMPLATE = '{}'

CHILD_TEMPLATE = r'''{
  "xhr": false
}'''

RECURSION = r'''{
  "name": "1",
  "kids": [{
    "name": "1.1",
    "kids": [{
      "name": "1.1.1"
    }]
  }]
}'''

COMMENTS = '{}'


ref_contexts = {}
for name, json_source in globals().items():
    if not name.isupper():
        continue
    ref_contexts[name.lower()] = json_source


if __name__ == '__main__':
    print 'known contexts:', ref_contexts.keys()
