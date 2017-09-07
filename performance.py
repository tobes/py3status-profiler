# -*- coding: utf-8 -*-
"""
py3status profiler.

run py3status for a set amount of time
a special test config is used tests/perf.conf
a mainly a testing module found in tests/perf.py
"""

from __future__ import print_function, division

import argparse
import os
import subprocess
import shlex
import sys

from time import sleep, time
from signal import SIGTERM

try:
    import psutil
except ImportError:
    psutil = None

import py3status

BASE_COMMAND = '{root}/__init__.py {split} -c {config} -i {module_dir} -l {log}'

PROFILERS = {
    'none': '{python} {cmd}',
    'cprofile': '{python} -m cProfile -o {output} {cmd}',
    'pprofile': 'pprofile --out {output} {cmd}',
    'vmprof': '{python} -m vmprof -o {output} {cmd}',
}

BLOCKS = u' ▏▎▍▌▋▊▉█'

FORMAT = u'\r{bar} {percent:6.2f}% {output_time}  ({p_time:.2f})'
FORMAT_NO_PSUTIL = u'\r{bar} {percent:6.2f}% {output_time}'


def profile(options):

    run_duration = options.time

    py3status_root = os.path.dirname(os.path.abspath(py3status.__file__))

    root = os.path.dirname(os.path.abspath(__file__))

    config = options.config
    if not config:
        config = os.path.join(root, 'configs', 'perf.conf')

    module_dir = os.path.join(root, 'modules')

    if options.profiler in ['none', 'cprofile']:
        split = ''
    else:
        split = '--'

    command = BASE_COMMAND.format(
        split=split,
        config=config,
        module_dir=module_dir,
        log=options.log,
        root=py3status_root,
    )

    profiler = PROFILERS[options.profiler]

    cmd = profiler.format(
        python=options.python,
        output=options.output,
        cmd=command
    )

    try:
        # turn off cursor
        print("\033[?25l", end='')

        mins = run_duration // 60
        if mins:
            mins = ' %d minutes' % mins
        else:
            mins = ''

        seconds = run_duration % 60
        if seconds:
            seconds = ' %d seconds' % seconds
        else:
            seconds = ''

        print('Running tests for{mins}{seconds}.'.format(
            mins=mins, seconds=seconds
        ))

        fnull = open(os.devnull, 'w')
        # start process and pass to psutil to get timings
        p = subprocess.Popen(shlex.split(cmd),
                             stdout=fnull,
                             stderr=subprocess.PIPE)
        if psutil:
            ps = psutil.Process(p.pid)
            format = FORMAT
        else:
            format = FORMAT_NO_PSUTIL

        # get the tty width so we can size the progress bar
        columns = int(os.popen('stty size', 'r').read().split()[1])
        start = time()
        p_time = None

        bar_len = columns - 30

        while True:

            t = time() - start
            t_int = int(t)

            if psutil:
                try:
                    cpu_time = ps.cpu_times()
                except psutil.NoSuchProcess:
                    break

                p_time = cpu_time.user + cpu_time.system

            # time as mins:secs
            output_time = '%3d:%02d' % (t_int // 60, t_int % 60)

            # percent of time done
            t_perc = t / run_duration
            percent = min(t_perc * 100, 100)

            # build the progress bar
            b = bar_len * t_perc
            b_int = int(b)

            partial = int(8 * ((b - b_int)))
            partial = BLOCKS[partial]
            bar = '[' + (u'█' * b_int) + partial + (' ' * (bar_len - b_int)) + ']'

            output = format.format(
                bar=bar,
                percent=percent,
                output_time=output_time,
                p_time=p_time,
            )

            # output and flush so visible to user
            print(output, end='')
            sys.__stdout__.flush()

            # check if we are done
            if t_int >= run_duration:
                break
            if p.poll():
                print('An error occured')
                print(p.stderr.read())
                break

            # take things easy
            sleep(0.2)

    except KeyboardInterrupt:
        pass
    finally:
        # turn cursor back on
        print("\033[?25h")

    if psutil:
        try:
            cpu_time = ps.cpu_times()
            print('user {}s'.format(cpu_time.user))
            print('system {}s'.format(cpu_time.system))
            print('total {}s'.format(cpu_time.system + cpu_time.user))

            # put py3status to bed
            ps.send_signal(SIGTERM)
        except psutil.NoSuchProcess:
            # process terminated
            print('Test terminated')


def main():
    parser = argparse.ArgumentParser(
        description='Run py3status for testing')
    parser = argparse.ArgumentParser(add_help=True)

    parser.add_argument(
        '-c',
        '--config',
        action="store",
        dest="config",
        type=str,
        default='',
        help="config file."
    )

    parser.add_argument(
        '-l',
        '--log',
        action="store",
        dest="log",
        type=str,
        default='/tmp/py3status_test.log',
        help="log file."
    )

    parser.add_argument(
        '-p',
        '--profiler',
        action="store",
        dest="profiler",
        type=str,
        choices=['none', 'cprofile', 'pprofile', 'vmprof'],
        default='none',
        help="type of profiler"
    )

    parser.add_argument(
        '-t',
        '--time',
        action="store",
        dest="time",
        type=int,
        default=600,
        help="number of seconds to run test for."
    )

    parser.add_argument(
        '--python',
        action="store",
        dest="python",
        type=str,
        default='python3',
        help="python version to use"
    )

    parser.add_argument(
        '-o',
        '--output',
        action="store",
        dest="output",
        default='/tmp/py3status.test.output',
        help="output file."
    )

    options = parser.parse_args()
    profile(options)


if __name__ == '__main__':
    main()
