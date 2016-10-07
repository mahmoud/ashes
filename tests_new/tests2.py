import ashes
from ashes import AshesEnv
ashes_env = AshesEnv()


template_string = """<html>
<body>
<p>Hello, {name}!</p>
</body>
</html>
{?one}{one}{/one}
{#names}{.}{~n}{/names}
{#person foo=root}{foo}: {name}, {age}{/person}
"""

ashes_env.register_source('test1', template_string)
template_data = {
  "name": 'world', 
  "one": 0,
  "names": ["Moe",
            "Larry",
            "Curly",
            ],
  "root": "Subject",
  "person": {"name": "Larry",
             "age": 45,
             },
  "name2": "1",
  "kids": [{"name": "1.1",
            "kids": [{"name": "1.1.1",
                      }
                     ]
            }
           ],
}

import time

ts = time.time()
for i in range(0, 100):
    ashes_env.render('test1', template_data)
tf = time.time()


print tf-ts
