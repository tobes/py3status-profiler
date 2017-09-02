A simple way to profile [py3status](https://github.com/ultrabug/py3status)

Supports the following if installed

* [cProfile](https://docs.python.org/2/library/profile.html#module-cProfile)

* [pprofile](https://github.com/vpelletier/pprofile)

* [vmprof](https://vmprof.readthedocs.io/en/latest/)

Optional dependency [psutil](https://pythonhosted.org/psutil/)

Example usage
```
python performance.py --python=python --profiler=pprofile -o ./cachegrind.out.test
```

For more details see

```
python performance.py --help
```
