import datetime
import inspect
import functools
import hashlib


class cached(object):
    """Decorator that caches a function's or class method's return value for cache_time_seconds.
    If called later before cache_time_seconds passed, the cached value is returned, and
    not re-evaluated.
    """

    def __init__(self, cache_time_seconds, print_if_cached=None, evaluate_on_day_change=False):
        """
        :param cache_time_seconds: cache time
        :param evaluate_on_day_change: re-evaluate if current day is not the same as cached value
        :param print_if_cached: if specified the string will be printed if cached value returned.
                                Inside string can be '{time}' parameter.
        """
        super().__init__()
        self.cache_time_seconds = cache_time_seconds
        self.print_if_cached = print_if_cached
        self.evaluate_on_day_change = evaluate_on_day_change
        self.time = datetime.datetime.now() - datetime.timedelta(seconds=cache_time_seconds + 1)
        self.cache = {}

    def __call__(self, func):
        def cached_func(*args):
            hash = hashlib.sha256((func.__name__ + str(args)).encode('utf-8')).hexdigest()
            now = datetime.datetime.now()
            if hash not in self.cache:
                self.cache[hash] = {'time': now - datetime.timedelta(seconds=self.cache_time_seconds + 1)}
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            seconds_passed = (now - self.cache[hash]['time']).seconds
            last_call_day = self.cache[hash]['time'].replace(hour=0, minute=0, second=0, microsecond=0)
            if seconds_passed < self.cache_time_seconds \
                    and (today == last_call_day or not self.evaluate_on_day_change):
                if self.print_if_cached:
                    print(self.print_if_cached.format(time=self.cache[hash]['time']))
            else:
                self.cache[hash]['value'] = func(*args)
                self.cache[hash]['time'] = now
                print('calculate ', hash)
            return self.cache[hash]['value']
        return cached_func

    def __get__(self, obj, objtype):
        return functools.partial(self.__call__, obj)


if __name__ == '__main__':
    import time

    class F(object):
        def __init__(self, n):
            self.n = n

        @cached(cache_time_seconds=1, print_if_cached='cached f at {time}')
        def f1(self, n):
            """fibonacci docstring"""
            if n in (0, 1):
                return n
            return (n-1) + (n-2)

        @cached(cache_time_seconds=1.1, print_if_cached='cached f2 at {time}')
        def f2(self, n):
            return n * self.n

    @cached(cache_time_seconds=1.2, print_if_cached='cached f3 at {time}')
    def f3(n):
        return n

    f=F(10)
    print(f.f1(1))
    #time.sleep(2)
    print(f.f1(1))
    print(f.f2(5))
    print(f.f2(5))
    f=F(20)
    print(f.f2(5))
    print(f.f1(100))
    print(f3(15))
    print(f3(15))
    print("__doc__: ", f.__doc__)
    print("__name__: ", f.f1.__name__)
