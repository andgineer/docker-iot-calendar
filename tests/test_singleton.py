from singleton import Singleton


def test_singleton_meta():
    class MyClass(metaclass=Singleton):
        pass

    class AnotherClass(metaclass=Singleton):
        def __init__(self, value):
            self.value = value

    obj1 = MyClass()
    obj2 = MyClass()

    # Assert that two instances are the same for the same class
    assert obj1 is obj2

    obj3 = AnotherClass(10)
    obj4 = AnotherClass(20)

    # Assert that two instances are the same even with different initial values
    assert obj3 is obj4
    assert obj3.value == 10

    # Assert that instances of different classes are different
    assert obj1 is not obj3

    # Resetting instances
    MyClass.new_instance()
    obj5 = MyClass()

    # Assert that the new instance is different from the old one
    assert obj1 is not obj5


def test_singleton_new_instance():
    class MyClassC(metaclass=Singleton):
        pass

    objC1 = MyClassC()
    objC2 = MyClassC.new_instance()

    # Ensure that the objects are different after using new_instance
    assert objC1 is not objC2
