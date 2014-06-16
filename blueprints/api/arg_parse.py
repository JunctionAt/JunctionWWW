

def argument_metaclass(class_name, parents, attributes):
    type(class_name, parents, attributes)


class ArgumentParser(object):
    __metaclass__ = type

    @classmethod
    def parse(cls, request):
        pass


class BaseArgument(object):
    pass


class StringArgument(BaseArgument):
    pass


class Test(ArgumentParser):
    uuid = StringArgument()