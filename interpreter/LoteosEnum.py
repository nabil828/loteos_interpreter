from aenum import Enum, auto


class CommandType(Enum):
    ASSERT = auto()
    GET_COMMAND = auto()
    PUT_COMMAND = auto()
    REMOVE_COMMAND = auto()
    LOCK_COMMAND = auto()
    UNLOCK_COMMAND = auto()


class ConsistencyType(Enum):
    SC = auto()
    EC = auto()
    MC = auto()


class CommandContainer:
    """
    For the thin client
    """
    def __init__(self, cmd, key, value):
        self.command = cmd
        self.key = key
        self.value = value
