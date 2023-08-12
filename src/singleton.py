"""Singleton meta class.
"""


class Singleton(type):
    """Singleton meta class.

    Usage: class YourClass(metaclass=Singleton)
    For this class only one instance will be created.
    All other YourClass() will return the same instance.

    To create new instance use YourClass.new_instance()
    """
    _instances = {}
    def __call__(cls, *args, **kwargs):
        """Call method."""
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def new_instance(cls):
        """Recreate instance for the class even it had been already created."""
        cls._instances.pop(cls, None)
        return cls()
