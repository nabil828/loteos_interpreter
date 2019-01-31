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
