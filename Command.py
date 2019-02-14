__author__ = 'Owner'
from LotoesCommandError import LotoesCommandError

# Two groups waiting for a reply with a value
# PUT, REMOVE, SHUTDOWN, JOIN, PING, PUT_HINTED, REMOVE_HINTED
# GET, GET_HINTED, PUSH, ALIVE

PUT = 0x01
GET = 0x02
REMOVE = 0x03

LOCK = 0x46
UNLOCK = 0x47


REGISTER = 0x48
SUBSCRIBE = 0x49
PUBLISH = 0x50
NOTIFY = 0x51


def print_command(x):
    if x == 0x01:
        return "PUT"
    elif x == 0x02:
        return "GET"
    elif x == 0x03:
        return "REMOVE"
    elif x == 0x46:
        return "LOCK"
    elif x == 0x47:
        return "UNLOCK"

    elif x == 0x48:
        return "REGISTER"
    elif x == 0x49:
        return "SUBSCRIBE"
    elif x == 0x50:
        return "PUBLISH"
    elif x == 0x51:
        return "NOTIFY"
    else:
        raise  LotoesCommandError("Unsupported command")
