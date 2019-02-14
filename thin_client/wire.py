__author__ = 'Owner'
import RequestReplyClient
import RequestReplyServer
import struct
import Command
import Response
# import binascii
# import Colors
import NodeList
import Print


class Wire:
    description = "This is implemented on top of the request/reply protocol you developed for A1 " \
                  "(i.e., using UDP, the process for unique IDs, timeouts, etc). " \
                  " The following describes the format of the application level messages exchanged using that protocol"
    numberOfNodes = 0
    hashedKeyModN = -1
    fmtRequest = "<B32s"  # Format of Data to be cont. later in the function
    fmtReply = "<B"
    # mode = ""
    # ALIVE_PUSH_DEBUG = False
    # REPLICATE_DEBUG = True

    successor = []

    def __init__(self, number_of_nodes):
        self.numberOfNodes = number_of_nodes

        # # Server
        # self.receiving_port = receiving_port
        # self.RequestReplyServer_obj = RequestReplyServer.RequestReplyServer(9999999, receiving_port,
        #                                                                     )  # listen infinitely

        # Client
        self.RequestReplyClient_obj = None

    def send_request(self, command, key, value_length, value, timeout=.1, retrials=2):  # by default retrials 2
        fmt = self.fmtRequest

        if command == Command.PUT or command == Command.PUBLISH or command == Command.SUBSCRIBE:
            fmt += "H" + str(value_length) + 's'

            msg = struct.pack(fmt, command, key, value_length, value)
        else:  # other commands like get
            msg = struct.pack(fmt, command, key)

        #  Get the IP Port from the key
        ip_port = NodeList.look_up_node_id(hash(key) % self.numberOfNodes)

        port = ip_port.split(':')[1]
        self.RequestReplyClient_obj = RequestReplyClient.RequestReplyClient(ip_port.split(':')[0],
                                                                            port,
                                                                            msg,
                                                                            timeout,
                                                                            retrials)

        self.RequestReplyClient_obj.send()
        Print.print_("send_request$ command:" + Command.print_command(command) \
                     + ", key: " + key \
                     + ", value_length: " \
                     + str(value_length) \
                     + ", value: " + str(value) \
                     , self.hashedKeyModN)

    def receive_reply(self, command):
        request_reply_response = self.RequestReplyClient_obj.receive_reply(command)
        # print "request_reply_response" , request_reply_response
        value = ("",)
        version = ""
        if request_reply_response == -1:
            response_code = Response.RPNOREPLY
        else:
            # try:
            response_code = struct.unpack(self.fmtReply, request_reply_response[0:1])
            response_code = response_code[0]
            # print "response_code", response_code
            if response_code == Response.SUCCESS:
                if len(request_reply_response) > 1:
                    value_length = struct.unpack('H', request_reply_response[1:3])
                    value_length = value_length[0]
                    if value_length != 0:  # operation is successful and there is a value.
                        value_fmt = str(value_length) + 's'
                        value = struct.unpack(value_fmt, request_reply_response[3:3 + value_length])
                        # if command == Command.GET or command == Command.PUT or command == Command.REMOVE:  # new
                        version_value_length = struct.unpack('H', request_reply_response[
                                                                  3 + value_length:3 + value_length + 2])
                        version_value_length = version_value_length[0]
                        version_fmt = str(version_value_length) + 's'
                        version = struct.unpack(version_fmt, request_reply_response[
                                                             3 + value_length + 2:3 + value_length + 2 + version_value_length])
        Print.print_("receive_reply$ response:" + Response.print_response(response_code) +
                     ", value:" + str(value[0]) +
                     ", command: " + Command.print_command(command)
                     , self.hashedKeyModN)
        return response_code, value[0], version
