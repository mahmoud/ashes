Below is a listing of all the Dust.JS improvements from the LinkedIn fork.

If a feature is concerned with the JS implementation, it should be marked as NA (Not Available)

Otherwise it should be marked with:

* PullRequest ID if pending
* + for supported
* x for "will not be supported"

======

Release 1.0.0 - Core enhancements

[PR15]  Extend partials to support inline params like #sections
[ ] Section index for lists of objects,$idx in the context
[ ] Section size/length for lists of objects, $len in the context
[ ] Extend grammar to relax whitespace/eol for certain Dust tags
[ ] Support numbers in the inline params
[ ] Extend core support for accessing single dimensional array with [] notation
[ ] Support dynamic blocks, similar to dynamic partials
[NA] Add pipe support for Node.js
[NA] Add support for runnin on V8/rhino
[ ] Extend filters for JSON.stringify and JSON.parse
[NA] Jasmine for unit tests


Release 1.0.0 - Bug fixes/ perf improvements

[NA] Fix to support > node0.4
[NA] Fix to peg.js to print the line and column number for syntax errors in dust templates
[NA]Improved compile times by 10X by optimizing the way we used the peg parser


Release 1.0.0 - Extensions and helpers

[ ] Simple logic/branching helpers with @select/ @eq/ @lt etc
[ ] Versatile @if helper relies on the eval for complex expression evaluation, Here are the perf results for eval http://jsperf.com/dust-if. Use with caution, since eval is known to be slow.


Release 1.1.0 - Core enhancements

[ ] Extend the #section block to support $idx and $len for lists of primitives
[ ] Add support for assigning multiple event-listeners on stream


Release 1.1.0 - Bug fixes/ perf improvements

[ ] Fix the #section block on how it behaves with empty arrays. Maintain consistency between ?, # and ^ for truthy/falsy evaluations
[ ] Fix "this" value in anonymous functions passed into the context object
[ ] Handle undefined filters and helpers gracefully

Release 1.1.0 - Extensions and helpers

[NA] Helpers are now in its own node package See here
[ ] @math for simple math operations such as add/subtract/mod/ceil etc. It also supports branching based on the output of math operation
[ ] @size helper for determining the size of lists/objects/primitives
[ ] @contextDump helper for debugging the current context in the dust stack


Release 1.2.0 - Core enhancements

[ ] GH- 166 - Added trimming of white spaces in dust templates configuration in the dust.compile ( default option is still true)


Release 1.2.0 - Bug fixes/ perf improvements

[ ] GH-148 - Fix the array reference access with $idx
[ ] GH-187 - Whitespace grammar rule for partial is now consistent with ther tags
[ ] GH-203 - Doc updated
[?] GH-212 - jam support for dust
[?] GH-216 - Add missing semicolon to help with minify
[?] GH-220 - Reverted in V1.2.1
[?] GH-222 - Fix regression add back $idx within a nested object in an array


Release 1.2.0 -Test enhancements

[ ] Tests's description updated to be more descriptive.
[ ] Bug fixes and UI improved.
[ ] Tests grouped by category


Release 1.2.1 - Bug fixes

[?] GH-220 - Reverted in V1.2.1 because of functional issues it introduced


Release 1.2.2 - Bug fixes

[NA] GH-245: solve incorrect error line reported in pegjs
[?] GH-241: using dust.isArray in place of Array.isArray


Release 1.2.3 - Perf Improvements for IE7

[NA] PR-253: performance enhancement in IE7


Release 2.0.0 - Core Enhancements

[PENDING:jvanasco] PR-305 change the default getPath behaviour to walk up the context tree
[ ] GH-292,GH-266 support storing the current template name in the global context
[NA] PR-295, upgrade jasmine-node to work with node 0.10
[ ] PR-278, remove the strip option that was added in previous releases
[ ] PR-263, enhanced |j filter


Release 2.0.0 - Bug fixes

[ ] PR-289, fix the CacheVM context across `dust.loadSource` calls for node.js



Release 2.0.2, (2.0.1)

[ ] 2.0.1.add line and column numbers in to the parser so we can use it in linters or debuggers
[ ] 2.0.2 actually uses it when using dust.parse


Release 2.0.3

[ ] PR-323, GH-322 - dynamic blocks {+"{dynam}"} has been corrected. It was adding the data twice.
[ ] GH-328 - move template name from global to the context


Release 2.1.0

[ ] PR-350 - Support dynamic template names for the context's template name.
[ ] PR-347, GH-137 - Improve JS debugging support for dust


Release 2.2.0

[ ] PR-360 - Use get for all Dust references.


Release 2.2.2

[ ]  PR-368 - Add context.getTemplateName. This method now correctly returns the template name even for directly loaded templates being used as partials. For end users please use this api for getting the template name instead of ctx.templatename.

Release 2.2.3

[ ] PR-363, GH-340 - Remove old optimization to avoid looking at arrays in get.

