import datetime
import functools
import hashlib
import inspect


class cached(object):
    """Decorator that caches a function's or class method's return value for cache_time_seconds.
    If called later before cache_time_seconds passed with the same arguments, the cached value
    is returned, and not re-evaluated.

    It compares hash of all function's arguments (str representation), and __init__ argumets of the
    object instance if this is class method.
    If you change something in object instance aside of function arguments and __init__ arguments,
    the decorator would not see that.

    Decorator instance is one per decorated class, so we need to take in account only __init__
    arguments, for other class will be other decorator instance.
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
        def cached_func(*args, **kw):
            #todo if this is function (no object method) and first argument is object,
            #we will use __dict__ of it - may be better to understand that this is not class method?
            if len(args) and hasattr(args[0], '__dict__'):
                hash_list = [str(args[0].__dict__), func.__name__, str(args[1:]), str(kw)] # __init__ params so we see if object created with different parameters
            else:
                hash_list = ['', func.__name__, str(args), str(kw)]
            hash = hashlib.sha256('\n'.join(hash_list).encode('utf-8')).hexdigest()
            now = datetime.datetime.now()
            for item in list(self.cache): # we have to keep cache clean
                if (now - self.cache[item]['time']).total_seconds() > self.cache_time_seconds:
                    del self.cache[item]
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            if hash in self.cache \
                    and (today == self.cache[hash]['time'].replace(hour=0, minute=0, second=0, microsecond=0)
                            or not self.evaluate_on_day_change):
                if self.print_if_cached:
                    print(self.print_if_cached.format(time=self.cache[hash]['time']))
            else:
                self.cache[hash] = {
                    'value': func(*args, **kw),
                    'time': now
                }
            return self.cache[hash]['value']
        return cached_func

    def __get__(self, obj, objtype):
        return functools.partial(self.__call__, obj)


def test():
    import time

    class F(object):
        def __init__(self, n):
            self.n = n

        @cached(cache_time_seconds=0.01, print_if_cached='returned cached f1 at {time}')
        def f1(self, n):
            if n in (0, 1):
                return n
            return (n-1) + (n-2)

        @cached(cache_time_seconds=0.05, print_if_cached='returned cached f2 at {time}')
        def f2(self, n):
            return n * self.n

    @cached(cache_time_seconds=0.07, print_if_cached='returned cached f3 at {time}')
    def f3(n):
        return n

    class F2(object):
        def __init__(self, n):
            self.n = n
        @cached(cache_time_seconds=0.05, print_if_cached='returned cached F2.f2 at {time}')
        def f2(self, n):
            return n * self.n

    class F3(object):
        @cached(cache_time_seconds=0.05, print_if_cached='returned cached F3.f2 at {time}')
        def f1(self, n):
            if n in (0, 1):
                return n
            return (n-1) + (n-2)

    f = F(10)
    assert f.f1(1) == 1
    assert f.f1(1) == 1 # should be cached
    assert f.f2(5) == 50
    time.sleep(0.2)
    assert f.f1(1) == 1
    assert f.f2(5) == 50
    assert f.f2(5) == 50 # should be cached
    time.sleep(0.1)
    assert f.f2(5) == 50
    f = F(20)
    assert f.f2(5) == 100
    assert f.f1(100) == 197
    f = F(20)
    assert f.f2(5) == 100 # should be cached
    assert f.f1(100) == 197 # should be cached
    f = F(10)
    assert f.f2(5) == 50 # should be cached
    assert f.f1(100) == 197
    assert f3(15) == 15
    assert f3(15) == 15 # should be cached
    f = F2(10)
    assert f.f2(5) == 50
    assert f.f2(5) == 50 # should be cached
    time.sleep(0.1)
    assert f.f2(5) == 50
    f = F3()
    assert f.f1(100) == 197
    assert f.f1(100) == 197 # should be cached
    print('should be 8 cached calls')


if __name__ == '__main__':
    test()

