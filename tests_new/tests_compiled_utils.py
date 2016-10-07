""" This bit is about testing timed functions

the @timeit decorator can be applied to functions for timing

the `timed_stats` function will print a nice graph
the `print_timed` function just prints some row oriented data

"""
import time
import operator

timeditems = {}


def timeit(method):
    """decorator method for timing an internal function
    saves to `timeditems` package var
    statistics available via `ashes.print_timed`
    """

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if method.__name__ not in timeditems:
            timeditems[method.__name__] = []
        timeditems[method.__name__].append(te - ts)
        return result
    return timed


def print_timed():
    """displays timing statisics
    """
    for k in timeditems.keys():
        ttl = sum(timeditems[k])
        avg = float(ttl) / len(timeditems[k])
        print "%s\n\t-- ttl = %s\n\t-- avg = %s\n\t-- its = %s" % (k, ttl, avg, len(timeditems[k]))


def timed_stats():
    """displays timing statisics
    """
    data = []
    data = {}
    for k in timeditems.keys():
        total = sum(timeditems[k])
        sample_size = len(timeditems[k])
        data[k] = {
            'name': k,
            'total': total,
            'average': float(total) / sample_size,
            'sample_size': sample_size,
        }
    data_2 = sorted(data.values(), key=operator.itemgetter('total'))
    baseline = data_2[-1]
    template = "{0:25} | {1:25} | {2:25} | {3:25} | {4:25}"  # column widths: 8, 10, 15, 7, 10
    print template.format("test", "total", "average", "sample_size", "baseline")
    print template.format("----", "-----", "-------", "-----------", "--------")
    for idx, i in enumerate(data_2):
        baseline_shift = (i['total'] / baseline['total'])
        print template.format(i['name'], "{:12.8f}".format(i['total']), "{:12.8f}".format(i['average']), i['sample_size'], "{:.4%}".format(baseline_shift))
