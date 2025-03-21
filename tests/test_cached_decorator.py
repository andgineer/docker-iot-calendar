import sys
import time
from io import BytesIO, TextIOWrapper

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
        @cached(seconds=0.01, trace_fmt="returned cached f1 at {time}")
        def f1(self, n):
            return n if n in (0, 1) else (n - 1) + (n - 2)

        @cached(seconds=0.05, trace_fmt="returned cached f2 at {time}")
        def f2(self, n):
            return n * self.n

    @cached(seconds=0.07, trace_fmt="returned cached f3 at {time}")
    def f3(n):
        return n

    class F2(object):
        def __init__(self, n):
            self.n = n

        @cached(seconds=0.05, trace_fmt="returned cached F2.f2 at {time}")
        def f2(self, n):
            return n * self.n

    class F3(object):
        @cached(seconds=0.05, trace_fmt="returned cached F3.f2 at {time}")
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

    assert len([line for line in out.split("\n") if line]) == hits


call_count = 0


def test_cache_decorator():
    global call_count

    @cached(seconds=0.1)
    def func(x, y):
        global call_count
        call_count += 1
        return x + y

    assert func(1, 2) == 3
    assert call_count == 1  # Ensure the function was called
    assert func(1, 2) == 3
    assert call_count == 1  # Ensure the function was cached and not called again


def test_cache_method_decorator():
    global call_count
    call_count = 0

    class MyClass:
        def __init__(self, x):
            self.x = x

        @cached(seconds=0.1)
        def add(self, y):
            global call_count
            call_count += 1
            return self.x + y

    obj = MyClass(1)
    assert obj.add(2) == 3
    assert call_count == 1
    assert obj.add(2) == 3
    assert call_count == 1


def test_cache_per_instance_decorator():
    global call_count
    call_count = 0

    class MyClass:
        def __init__(self, x):
            self.x = x

        @cached(seconds=0.1, per_instance=True)
        def add(self, y):
            global call_count
            call_count += 1
            return self.x + y

    obj1 = MyClass(1)
    assert obj1.add(2) == 3
    assert call_count == 1
    obj2 = MyClass(1)
    assert obj2.add(2) == 3  # Separate cache for obj2
    assert call_count == 2  # Because we expect obj2 to have its own cache


def test_shared_cache_between_instances():
    global call_count
    call_count = 0

    class MyClass:
        def __init__(self, x):
            self.x = x

        @cached
        def add(self, y):
            global call_count
            call_count += 1
            return self.x + y

    obj1 = MyClass(1)
    assert obj1.add(2) == 3
    assert call_count == 1
    obj2 = MyClass(1)
    assert obj2.add(2) == 3  # Uses cache from obj1
    assert call_count == 1  # Because obj1 and obj2 should share the cache


def test_func_cache():
    global call_count
    call_count = 0

    @cached(seconds=0.1)
    def add(y):
        global call_count
        call_count += 1
        return x + y

    x = 1
    assert add(2) == 3
    assert add(2) == 3
    assert call_count == 1
    x = 2
    assert add(2) == 3  # Uses cache from x=1
    assert call_count == 1


def test_func_without_args_cache():
    global call_count
    call_count = 0

    @cached
    def add(y):
        global call_count
        call_count += 1
        return x + y

    x = 1
    assert add(2) == 3
    assert add(2) == 3
    assert call_count == 1
    x = 2
    assert add(2) == 3  # Uses cache from x=1
    assert call_count == 1


counter = 0


@cached(seconds=1)
def func(x):
    global counter
    counter += 1
    return x


def test_clear_cache():
    global counter
    counter = 0

    # Call the function to store result in cache
    result1 = func(10)
    assert counter == 1

    # Call the function again without clearing the cache
    result2 = func(10)
    # Assert that the function is not re-evaluated
    assert counter == 1
    assert result1 == result2

    # Clear the cache and call the function again
    func.clear_cache()
    result3 = func(10)
    # Assert that the function is re-evaluated
    assert counter == 2
    assert result3 == 10


def test_cache_none():
    counter = [0]

    @cached(cache_none=False)
    def func1(x):
        counter[0] += 1
        return None if x == 0 else x

    @cached(cache_none=True)
    def func2(x):
        counter[0] += 1
        return None if x == 0 else x

    # Call func1 with x=0, the result will be None
    assert func1(0) is None
    assert counter[0] == 1

    # Call func1 again with x=0, the result should be re-evaluated because cache_none is False
    assert func1(0) is None
    assert counter[0] == 2

    # Call func2 with x=0, the result will be None
    assert func2(0) is None
    assert counter[0] == 3

    # Call func2 again with x=0, the result should be cached because cache_none is True
    assert func2(0) is None
    assert counter[0] == 3
