import time
from io import TextIOWrapper, BytesIO
import sys
from cached_decorator import cached


def test_cashed_decorator():


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

        # @second(1) Now I do not know how to make it work together with other decorators
        @cached(cache_time_seconds=0.01, print_if_cached='returned cached f1 at {time}')
        def f1(self, n):
            return n if n in (0, 1) else (n - 1) + (n - 2)

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
            return n if n in (0, 1) else (n - 1) + (n - 2)


    buf = BytesIO()
    sys.stdout = TextIOWrapper(buf, sys.stdout.encoding)

    hits = 0

    f = F(10)
    assert f.f1(1) == 1
    assert f.f1(1) == 1  # should be cached
    hits += 1
    assert f.f2(5) == 50
    time.sleep(0.2)
    assert f.f1(1) == 1
    assert f.f2(5) == 50
    assert f.f2(5) == 50  # should be cached
    hits += 1
    time.sleep(0.1)
    assert f.f2(5) == 50
    f = F(20)
    assert f.f2(5) == 100
    assert f.f1(100) == 197
    f = F(20)
    assert f.f2(5) == 100  # should be cached
    hits += 1
    assert f.f1(100) == 197  # should be cached
    hits += 1
    f = F(10)
    assert f.f2(5) == 50  # should be cached
    hits += 1
    assert f.f1(100) == 197
    assert f3(15) == 15
    assert f3(15) == 15  # should be cached
    hits += 1
    f = F2(10)
    assert f.f2(5) == 50
    assert f.f2(5) == 50  # should be cached
    hits += 1
    time.sleep(0.1)
    assert f.f2(5) == 50
    f = F3()
    assert f.f1(100) == 197
    assert f.f1(100) == 197  # should be cached
    hits += 1

    sys.stdout.seek(0)
    out = sys.stdout.read()
    sys.stdout = sys.__stdout__
    print(out)

    assert len([line for line in out.split('\n') if line]) == hits
