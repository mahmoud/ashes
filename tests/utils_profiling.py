import cProfile as profile
import pstats
import pprint
import sys
import os
import csv
import time

basedir = os.path.dirname(__file__)
basedir_len = len(basedir)

def format_fname(value, _sys_path=None):
    """from pyramid_debugtoolbar"""
    if _sys_path is None:
        _sys_path = sys.path # dependency injection
    # If the value is not an absolute path, the it is a builtin or
    # a relative file (thus a project file).
    if not os.path.isabs(value):
        if value.startswith(('{', '<')):
            return value
        if value.startswith('.' + os.path.sep):
            return value
        return '.' + os.path.sep + value


def profile_function(to_profile, filename_stats=None):
    """largely from pyramid_debugtoolbar"""
    profiler = profile.Profile()
    result = profiler.runcall(to_profile)
    stats = pstats.Stats(profiler)
    function_calls = []
    flist = stats.sort_stats('cumulative').fcn_list
    
    for func in flist:
        current = {}
        info = stats.stats[func]

        # Number of calls
        if info[0] != info[1]:
            current['ncalls'] = '%d/%d' % (info[1], info[0])
        else:
            current['ncalls'] = info[1]

        # Total time
        current['tottime'] = info[2] * 1000

        # Quotient of total time divided by number of calls
        if info[1]:
            current['percall'] = info[2] * 1000 / info[1]
        else:
            current['percall'] = 0

        # Cumulative time
        current['cumtime'] = info[3] * 1000

        # Quotient of the cumulative time divded by the number
        # of primitive calls.
        if info[0]:
            current['percall_cum'] = info[3] * 1000 / info[0]
        else:
            current['percall_cum'] = 0

        # Filename
        filename = pstats.func_std_string(func)
        current['filename_long'] = filename
        current['filename'] = format_fname(filename)
        function_calls.append(current)

    keys = function_calls[0].keys()
    if filename_stats:
        with open(filename_stats, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(function_calls)        
        print("wrote to %s" % filename_stats)
    else:
        print("returning (function_calls)")
        return function_calls
    