import numpy as np
import StringIO
import types
import sys
import time
from IPython import get_ipython

def dict_to_ordered_tuples(dic):
    '''Convert a dictionary to a list of tuples, sorted by key.'''
    if dic is None:
        return []
    keys = dic.keys()
    keys.sort()
    ret = [(key, dic[key]) for key in keys]
    return ret

def remove_dict_keys(dic, keys):
    for key in keys:
        if key in dic:
            del dic[key]

def get_dict_keys(dic, keys):
    ret = {}
    for key in keys:
        if key in dic:
            ret[key] = dic[key]
    return ret

def seconds_to_str(secs):
    '''Convert a number of seconds to hh:mm:ss string.'''
    hours = np.floor(secs / 3600)
    secs -= hours * 3600
    mins = np.floor(secs / 60)
    secs = np.floor(secs - mins * 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)

def pil_to_pixbuf(pilimage):
    '''Convert a PIL image to a pixbuf.'''
    import gtk

    data = StringIO.StringIO()
    pilimage.save(data, 'ppm')
    contents = data.getvalue()
    data.close()

    loader = gtk.gdk.PixbufLoader('pnm')
    loader.write(contents, len (contents))
    pixbuf = loader.get_pixbuf()
    loader.close()

    return pixbuf

def sign(val):
    '''Return the sign of a value.'''
    if val < 0:
        return -1
    else:
        return 1

def get_arg_type(args, kwargs, checktypes, name=None):
    '''
    Get first argument of a type in 'checktypes' (single type or list/tuple).
    If a specific name is specified, the kwargs dictionary is checked first.
    '''

    if name is not None and name in kwargs:
        return kwargs[name]

    if type(checktypes) not in (types.ListType, types.TupleType):
        checktypes = [checktypes]

    for arg in args:
        for checktype in checktypes:
            if isinstance(arg, checktype):
                return arg

    return None

_time_func = None
def exact_time():
    global _time_func
    if _time_func is None:
        if sys.platform in ['win32', 'cygwin']:
            _time_func = time.clock
        else:
            _time_func = time.time

    return _time_func()

def usleep(usec):
    '''
    Sleep for usec microseconds.
    '''
    start = exact_time()
    while (exact_time() - start) * 1e6 < usec:
        pass

def get_traceback():
    from IPython.core.ultratb import AutoFormattedTB
    return AutoFormattedTB

def is_ipython():
    return get_ipython() != None

def exit_shell():
    if is_ipython():
        ip = get_ipython()
        ip.exit() # FIXME This gives annoying request for y/n when called
    sys.exit()

def register_exit(func):
    if is_ipython():
        ip = get_ipython()
        ip.hooks['shutdown_hook'].add(func, 1)
    else:
        import atexit
        atexit.register(func)

