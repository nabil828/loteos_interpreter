__author__ = 'Owner'
import RequestReplyClient
import RequestReplyServer
import struct
import Command
import Exceptions
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

    def __init__(self, number_of_nodes, receiving_port):
        self.numberOfNodes = number_of_nodes

        # # Server
        self.receiving_port = receiving_port
        self.RequestReplyServer_obj = RequestReplyServer.RequestReplyServer(9999999, receiving_port)

        # # Client
        # self.RequestReplyClient_obj = None

    def receive_request(self):
        header, msg, addr, sixteen_byte_header = self.RequestReplyServer_obj.receive()
        command, key = struct.unpack(self.fmtRequest, msg[0:33])

        assert (command == Command.NOTIFY)
        value_length = struct.unpack("H", msg[33:35])
        value_length = int(value_length[0])
        value_fmt = str(value_length) + 's'
        value = struct.unpack(value_fmt, msg[35:35 + value_length])
        key = key.rstrip('\0')
        value = value[0]

        Print.print_("receive_request$ "
                     + str(addr)
                     + ", Command Received:"
                     + Command.print_command(command)
                     + ", Key:"
                     + key
                     + ", Value: "
                     + value
                     + ", Value Length: "
                     + str(value_length)
                     , self.hashedKeyModN)
        return command, key, value_length, value, addr, sixteen_byte_header

    def send_reply(self, sender_addr, key, response_code, value, command, sixteen_byte_header, origin_receiver=True):
        fmt = self.fmtReply
        msg = struct.pack(fmt, response_code)
        self.RequestReplyServer_obj.send_reply(sender_addr[0], sender_addr[1], msg, command, key, self.hashedKeyModN,
                                               sixteen_byte_header, origin_receiver)
        Print.print_("send_reply$ " + str(sender_addr) +
                     ", response_code: " + Response.print_response(response_code) +
                     ", value: " + value +
                     ", value length: " + str(len(value)) +
                     ", command: " + Command.print_command(command)
                     , self.hashedKeyModN)
