"""
Thin client for Loteos Key value store
"""

import threading
# import sys
# from os import path
# sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from . import wire
from .LoteosThinClientSupport import ResponseObj, outgoing_requests_q, response_q
# sys.path.append('../Command.py')
wireObj = None


def settings(N):
    global wireObj
    wireObj = wire.Wire(int(N))


# user_input(2, queue_obj(Command.GET, key, ""));
def send_requests():
    """
    producer for outgoing_requests_q
    :return:
    """
    global wireObj

    while True:
        queue_obj = outgoing_requests_q.get()
        wireObj.send_request(queue_obj.command,
                             str(queue_obj.key),
                             len(str(queue_obj.value)),  # Todo add tostring() for your grammer
                             str(queue_obj.value),
                             .2,
                             0)
        response_code, response_value, version = wireObj.receive_reply(queue_obj.command)
        response_q.put(ResponseObj(response_code, response_value, version))


def start(_n):
    """
    ToDo link to resources that you need from loteos Kv store
    """
    global N
    # N = sys.argv[1]
    N = _n
    settings(N)

    user_input_thread = threading.Thread(target=send_requests)
    user_input_thread.setName('userInput thread')
    user_input_thread.start()
