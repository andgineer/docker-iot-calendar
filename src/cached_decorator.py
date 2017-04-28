import datetime
import functools
import hashlib


class cached(object):
    """Decorator that caches a function's or class method's return value for cache_time_seconds.
    If called later before cache_time_seconds passed with the same arguments, the cached value
    is returned, and not re-evaluated.
    Example of usage:
        @cached(0.1)
        def function_to_cash_for_one_tenth_of_second():

    ! For object method it should be the only decorator applied because it saves ref to decorated function
    and if it changed by other decorator it would treat method call as function call, and
    in this case without @singleton for the class it would cache different instances with different hashes.
    And would not use the object attributes in hash.

    All instances of the same class would be the same for cache decorator if they has the same
    attributes.
    So the object do not need to be singleton to be cached.
    For example:
        obj = MyObject(1)
        obj.my_func(2)
        obj.my_func(2) # cached
        obj2 = MyObject(1)
        obj2.my_func(2) # also cached
        obj3 = MyObject(2)
        obj3.my_func(2) # not cached, if MyObject __init__ save something different in self
                          # for different __init__ parameter

    It compares hash of all function's arguments (str representation),
    and __dict__ of it's first argument if it is an object with one of it's methods the same
    as decorated function.
    So if you change something in the object (any self.<attribute>), the decorator also
    would see that.
    !!! Str representations for function arguments should be distinguishable.
    That's true at list for python's list & dict.

    Decorator instance is one per decorated function/method, so we do not need to take into account
    function and object name (if this is object method), because for other functions/methods it will
    be other decorator instance.
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

    def is_self_in_args(self, args, func):
        first_arg_is_object = len(args) and hasattr(args[0], '__dict__') \
            and '__class__' in dir(args[0])
        return first_arg_is_object and func.__name__ in dir(args[0])\
                and '__func__' in dir(getattr(args[0], func.__name__)) \
                and getattr(args[0], func.__name__).__func__ == self.func

    def __call__(self, func):
        def cached_func(*args, **kw):
            if self.is_self_in_args(args, func):
                # the first argument is 'self', this is objects's method so add the object attributes
                # we do not use str representation because decorated object has id in it,
                # but I need the same hash for different instances with the same attributes.
                hash_list = [str(args[0].__dict__), str(args[1:]), str(kw)]
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
        self.func = cached_func
        return cached_func

    def __get__(self, obj, objtype=None):
        return functools.partial(self.__call__, obj)


def test():
    import time
    from io import TextIOWrapper, BytesIO
    import sys


    class second(object):
        def __init__(self, param):
            pass

        def __call__(self, func):
            def second_func(*args, **kw):
                return func(*args, **kw)
            return second_func

    class F(object):
        def __init__(self, n):
            self.n = n

        #@second(1) Now I do not know how to make it work together with other decorators
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


    buf = BytesIO()
    sys.stdout = TextIOWrapper(buf, sys.stdout.encoding)

    hits = 0

    f = F(10)
    assert f.f1(1) == 1
    assert f.f1(1) == 1 # should be cached
    hits += 1
    assert f.f2(5) == 50
    time.sleep(0.2)
    assert f.f1(1) == 1
    assert f.f2(5) == 50
    assert f.f2(5) == 50 # should be cached
    hits += 1
    time.sleep(0.1)
    assert f.f2(5) == 50
    f = F(20)
    assert f.f2(5) == 100
    assert f.f1(100) == 197
    f = F(20)
    assert f.f2(5) == 100 # should be cached
    hits += 1
    assert f.f1(100) == 197 # should be cached
    hits += 1
    f = F(10)
    assert f.f2(5) == 50 # should be cached
    hits += 1
    assert f.f1(100) == 197
    assert f3(15) == 15
    assert f3(15) == 15 # should be cached
    hits += 1
    f = F2(10)
    assert f.f2(5) == 50
    assert f.f2(5) == 50 # should be cached
    hits += 1
    time.sleep(0.1)
    assert f.f2(5) == 50
    f = F3()
    assert f.f1(100) == 197
    assert f.f1(100) == 197 # should be cached
    hits += 1

    sys.stdout.seek(0)
    out = sys.stdout.read()
    sys.stdout = sys.__stdout__
    print(out)

    assert len([line for line in out.split('\n') if line]) == hits

if __name__ == '__main__':
    test()

