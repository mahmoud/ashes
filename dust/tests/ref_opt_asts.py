from __future__ import unicode_literals

import json

CONDITIONAL = r'''["body",["?",["key","tags"],["context"],["params"],["bodies",["param",["literal","else"],["body",["buffer","No Tags!"]]],["param",["literal","block"],["body",["buffer","<ul>\n"],["#",["key","tags"],["context"],["params"],["bodies",["param",["literal","block"],["body",["buffer","  <li>"],["reference",["path",true,[]],["filters"]],["buffer","</li>\n"]]]]],["buffer","</ul>"]]]]],["buffer","\n"],["^",["key","likes"],["context"],["params"],["bodies",["param",["literal","else"],["body",["buffer","<ul>\n"],["#",["key","likes"],["context"],["params"],["bodies",["param",["literal","block"],["body",["buffer","  <li>"],["reference",["path",true,[]],["filters"]],["buffer","</li>\n"]]]]],["buffer","</ul>"]]],["param",["literal","block"],["body",["buffer","No Likes!"]]]]]]'''


ref_opt_asts = {}
for name, json_source in globals().items():
    if not name.isupper():
        continue
    ref_opt_asts[name.lower()] = json_source


if __name__ == '__main__':
    print 'known optimized ASTs:', ref_opt_asts.keys()
