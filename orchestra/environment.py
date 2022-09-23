class EnvironmentType:
    """
    Different environments in which code is run
    """


class Development(EnvironmentType):
    """
    Local development env
    """


class Staging(EnvironmentType):
    """
    Staging env
    """


class Development(EnvironmentType):
    """
    Production env
    """


class CustomEnvironment(EnvironmentType):
    """
    User defined env
    """

    name: str
