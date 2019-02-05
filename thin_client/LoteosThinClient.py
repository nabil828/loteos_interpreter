"""
Thin client for Loteos Key value store
"""

__author__ = 'Owner'

import NodeList
import sys
import threading
import Command
sys.path.insert(0, 'C:\loteos\\')
sys.path.insert(0, '../loteos')
import wire
from LoteosThinClientSupport import ResponseObj, incoming_requests_q, response_q

# local or planetlab
# global mode
# mode = mode_


ip_port = NodeList.look_up_node_id(hashedKeyModN)
receiving_port = ip_port.split(':')[1]
wireObj = wire.Wire(int(N), hashedKeyModN, mode, "main", receiving_port, successor_list)

global vector_stamp_table
vector_stamp_table = [0] * int(N)


# user_input(2, queue_obj(Command.GET, key, ""));
def user_input():  # producer for incoming_requests_q
    global wireObj

    while True:
        queue_obj = incoming_requests_q.get()
        wireObj.send_request(queue_obj.cmd, queue_obj.key, len(queue_obj.value), queue_obj.value, threading.currentThread(), node,
                                      .2, 0)
        response_code, response_value, version = wireObj.receive_reply(threading.currentThread(),
                                                                                Command.REPLICATE_GET)
        response_q.put(ResponseObj(response_code, response_value, version))


if __name__ == "__main__":
    """
    ToDo link to resources htat you need from loteos Kv store
    """
    global N
    N = sys.argv[1]

    userInputThread = threading.Thread(target=user_input)
    userInputThread.setName('userInput thread')
    userInputThread.start()
