import io
import pstats
import sys
import time
import threading

import pyprof2calltree
import yappi


def profile_yappi(output):
    yappi.start()

    from py3status.core import Py3statusWrapper
    try:
        py3 = Py3statusWrapper()
        py3.setup()
        py3.run()
    except KeyboardInterrupt:
        py3.stop()

    yappi.stop

    s = io.StringIO()
    ps = yappi.convert2pstats(yappi.get_func_stats())
    pyprof2calltree.convert(ps, output)


if __name__ == '__main__':
    # First arg is output filename.
    output=sys.argv[1]
    # next arg should be ignored
    sys.argv = sys.argv[2:]

    profile_yappi(output)
