"""Cache function or object method return value.

lru_cache was not used due to its lack of support for cache duration.
To be honest, this was implemented primarily for educational purposes.
"""
import datetime
import functools
import hashlib
from typing import Any, Callable, Dict, Optional, Tuple, Union

Func = Callable[..., Any]


class cached:
    """Decorator that caches a function's or class method's return value for cache_time_seconds.

    Usage:

        class C:
                @cached
                def f1()
                        pass
                @cached(per_instance=True)
                def f2()
                        pass

        @cached
        def f()
                pass

        @cached(seconds=1)
        def f2()
                pass

        f.clear_cache() # clear cache for f

    If called later before cache_time_seconds passed with the same arguments, the cached value
    is returned, and not re-evaluated.

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

    def __init__(
        self,
        func: Optional[Func] = None,
        *,
        seconds: Union[float, int] = 0.1,
        trace_fmt: Optional[str] = None,
        daily_refresh: bool = False,
        per_instance: bool = False,
        cache_none: bool = True,
    ) -> None:
        """Init.

        :param seconds: cache time
        :param daily_refresh: re-evaluate if current day is not the same as cached value
        :param trace_fmt: if specified the string will be printed if cached value returned.
                                Inside string can be '{time}' parameter.
        :param per_instance: if False in case of object method the same cache would be used for all instances
        :param cache_none: if False the function would be re-evaluated if cached value is None
        """
        super().__init__()
        self.cache_time_seconds = seconds
        self.print_if_cached = trace_fmt
        self.evaluate_on_day_change = daily_refresh
        self.time = datetime.datetime.now() - datetime.timedelta(seconds=seconds + 1)
        self.cache_per_instance = per_instance
        self.cache_none = cache_none
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.func = func

        if func:
            # @cached without arguments
            self.__call__ = self.decorate(func)  # type: ignore

    def is_self_in_args(self, args: Tuple[Any, ...], func: Func) -> bool:
        """Check if the first argument is object with the same method as decorated function."""
        if not args:
            return False
        first_arg = args[0]

        # Check if the first argument is an instance of a class
        if not isinstance(first_arg, object) or not hasattr(first_arg, "__dict__"):
            return False

        # Check if the first argument's class has the function as one of its methods
        if not hasattr(first_arg.__class__, func.__name__):
            return False  # todo check if it is the same function, not just the same name

        return True

    def __call__(self, *args: Any, **kwargs: Any) -> Any:  # pylint: disable=method-hidden
        """Call the decorated function/method.

        Replace the method in __init__ with self.decorate() for @cached without arguments.
        """
        if self.func:
            # If '@cached' is used without arguments
            return self.decorate(self.func)(*args, **kwargs)
        # If '@cached' is used with arguments
        # In this case, args[0] will be the decorated function/method.
        return self.decorate(args[0])

    def clear_cache(self) -> None:
        """Clear the cache."""
        self.cache = {}

    def decorate(self, func: Func) -> Func:
        """Decorate function."""

        def cached_func(*args: Any, **kw: Any) -> Any:
            """Cache function."""
            if self.is_self_in_args(args, func):
                # the first argument is 'self', this is objects's method so add the object attributes
                if self.cache_per_instance:
                    # Use object's id in the hash for separate instance caching
                    hash_list = [str(id(args[0])), str(args[0].__dict__), str(args[1:]), str(kw)]
                else:
                    hash_list = [str(args[0].__dict__), str(args[1:]), str(kw)]
            else:
                hash_list = ["", func.__name__, str(args), str(kw)]
            hash = hashlib.sha256("\n".join(hash_list).encode("utf-8")).hexdigest()
            now = datetime.datetime.now()
            for item in list(self.cache):  # we have to keep cache clean
                if (now - self.cache[item]["time"]).total_seconds() > self.cache_time_seconds:
                    del self.cache[item]
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            if hash in self.cache and (
                today
                == self.cache[hash]["time"].replace(hour=0, minute=0, second=0, microsecond=0)
                or not self.evaluate_on_day_change
            ):
                # cache hit and the day the same of no need to track day change
                if not self.cache_none and self.cache[hash]["value"] is None:
                    # Re-evaluate the function if cache_none is False and cached value is None
                    self.cache[hash] = {"value": func(*args, **kw), "time": now}
                else:
                    if self.print_if_cached:
                        print(self.print_if_cached.format(time=self.cache[hash]["time"]))
            else:
                self.cache[hash] = {"value": func(*args, **kw), "time": now}
            return self.cache[hash]["value"]

        self.func = cached_func
        cached_func._original_func = (  # type: ignore
            func  # Store the original function to be sure we decorate class
        )
        cached_func.clear_cache = self.clear_cache  # type: ignore  # Add clear_cache method to cached_func

        return cached_func

    def __get__(self, obj: Any, objtype: Optional[Any] = None) -> Func:
        """Descriptor protocol.

        To automatically bind the decorator's call to the object instance.
        """
        return functools.partial(self.__call__, obj)  # type: ignore
