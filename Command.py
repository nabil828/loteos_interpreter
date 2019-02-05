__author__ = 'Owner'
from thin_client.LotoesCommandError import LotoesCommandError

# Two groups waiting for a reply with a value
# PUT, REMOVE, SHUTDOWN, JOIN, PING, PUT_HINTED, REMOVE_HINTED
# GET, GET_HINTED, PUSH, ALIVE

PUT = 0x01
GET = 0x02
REMOVE = 0x03

LOCK = 0x46
UNLOCK = 0x47


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
    else:
        raise  LotoesCommandError("Unsupported command")
