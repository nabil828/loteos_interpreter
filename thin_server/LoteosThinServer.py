"""
Thin server for Loteos pub/sub coordination service
"""

import threading
# import sys
# from os import path
# sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from . import wire
import Response
# sys.path.append('../Command.py')
wireObj = None
import NodeList
from LoteosThinServerSupport import incoming_requests_q
import pickle


def settings(N, node_id):
    global wireObj
    ip_port = NodeList.look_up_node_id(node_id)
    receiving_port = ip_port.split(':')[1]
    wireObj = wire.Wire(int(N), receiving_port)


# user_input(2, queue_obj(Command.GET, key, ""));
def receive_requests():
    """
    # consumer for incoming_requests_q
    :return:
    """
    global wireObj

    while True:
        # print "server: waiting for requests .."
        command, key, value_length, value, sender_addr, sixteen_byte_header = wireObj.receive_request()
        value = pickle.loads(value)
        incoming_requests_q.put(value)
        wireObj.send_reply(
            sender_addr,
            key,
            Response.SUCCESS,
            str(""),
            command,
            sixteen_byte_header
        )


def start(_n, node_id):
    """
    """
    global N
    # N = sys.argv[1]
    N = _n
    settings(N, node_id)

    user_input_thread = threading.Thread(target=receive_requests)
    user_input_thread.setName('userInput thread')
    user_input_thread.start()
