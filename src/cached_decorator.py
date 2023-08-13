"""Cache function or object method return value.

lru_cache was not used due to its lack of support for cache duration.
To be honest, this was implemented primarily for educational purposes.
"""
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
    in this case if the class is not singleton it would cache different instances with different hashes.
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

    def __init__(self, cache_time_seconds, print_if_cached=None, evaluate_on_day_change=False, cache_per_instance=False):
        """Init.

        :param cache_time_seconds: cache time
        :param evaluate_on_day_change: re-evaluate if current day is not the same as cached value
        :param print_if_cached: if specified the string will be printed if cached value returned.
                                Inside string can be '{time}' parameter.
        :param cache_per_instance: if False in case of object method the same cache would be used for all instances
        """
        super().__init__()
        self.cache_time_seconds = cache_time_seconds
        self.print_if_cached = print_if_cached
        self.evaluate_on_day_change = evaluate_on_day_change
        self.time = datetime.datetime.now() - datetime.timedelta(seconds=cache_time_seconds + 1)
        self.cache_per_instance = cache_per_instance
        self.cache = {}

    def is_self_in_args(self, args, func):
        """Check if the first argument is object with the same method as decorated function."""
        first_arg_is_object = len(args) and hasattr(args[0], '__dict__') \
            and '__class__' in dir(args[0])
        return first_arg_is_object and func.__name__ in dir(args[0])\
                and '__func__' in dir(getattr(args[0], func.__name__)) \
                and getattr(args[0], func.__name__).__func__ == self.func

    def __call__(self, func):
        """Call decorator."""
        def cached_func(*args, **kw):
            """Cached function."""
            if self.is_self_in_args(args, func):
                # the first argument is 'self', this is objects's method so add the object attributes
                if self.cache_per_instance:
                    # Use object's id in the hash for separate instance caching
                    hash_list = [str(id(args[0])), str(args[0].__dict__), str(args[1:]), str(kw)]
                else:
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

    def clear_cache(self):
        """Clear cache."""
        self.cache = {}

