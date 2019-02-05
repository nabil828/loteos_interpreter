__author__ = 'Owner'
import RequestReplyClient
import RequestReplyServer
import struct
import Command
import Response
# import binascii
# import Colors
import NodeList
import Mode
import Print
# import Settings
import VectorStamp
import Settings
import sys

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

    def __init__(self, number_of_nodes, hashedKeyModN, mode, id_, receiving_port=-1, successor=[-1, -1],
                 middle_sender_addr=None):
        self.numberOfNodes = number_of_nodes
        self.hashedKeyModN = hashedKeyModN  # Local node only
        self.mode = mode
        self.successor = successor
        self.id = id_  # just to have separate port for alive and push msgs

        # Server
        self.receiving_port = receiving_port
        self.RequestReplyServer_obj = RequestReplyServer.RequestReplyServer(9999999, id_, receiving_port,
                                                                            middle_sender_addr)  # listen infinitely

        # Client
        self.RequestReplyClient_obj = None

    def send_request(self, command, key, value_length, value, cur_thread, node_overwrite, timeout=.1,
                     retrials=2):  # by default retrials 2
        fmt = self.fmtRequest

        if command == Command.JOIN_SUCCESSOR:
            print ''
        vector_stamp_value = ''
        vector_stamp_value_length = 0
        # advance the local time
        # if command == Command.PUT or command == Command.REPLICATE_PUT or command == Command.REPLICATE_GET or command == Command.REPLICATE_REMOVE or command == Command.GET or command == Command.REMOVE :
        if command == Command.COMMIT:
            VectorStamp.advance_local_time_stamp()

            vector_stamp_value = VectorStamp.to_string()
            vector_stamp_value_length = len(vector_stamp_value)
            # print "vector_stamp_value_length:" + str(
            #     vector_stamp_value_length) + "  , vector_stamp_value:" + str(vector_stamp_value)
            fmt += "HH" + str(value_length) + 's' + str(vector_stamp_value_length) + 's'
            msg = struct.pack(fmt, command, key, value_length, vector_stamp_value_length, value, vector_stamp_value)

        elif command == Command.PUT or command == Command.JOIN_SUCCESSOR or command == Command.JOIN_PREDECESSOR or\
                command == Command.ALIVE or command == Command.PUSH or command == Command.REPLICATE_PUT or \
                command == Command.EXECUTE or command == Command.REPLICATE_EXECUTE or \
                command == Command.EXECUTE_HINTED or command == Command.REPLICATE_GET or command == Command.DISTRIBUTE\
                or command == Command.START_TEST:
            fmt += "H" + str(value_length) + 's'
            # fmt += "HH" + str(value_length) + 's' + str(vector_stamp_value_length) + 's'
            msg = struct.pack(fmt, command, key, value_length, value)
        # elif command == Command.DISTRIBUTE:
        #     vector_stamp_string = Settings.get_vector_stamp_string()
        #     vector_stamp_string_length = len(vector_stamp_string)
        #     fmt += "H" + str(value_length) + 's'
        #     fmt += "H" + str(vector_stamp_string_length) + 's'
        #     msg = struct.pack(fmt, command, key, value_length, value, vector_stamp_string_length, vector_stamp_string)
        else:  # other commands like get, PING
            # fmt += '0s'  # hope to receive value of null with length 1
            msg = struct.pack(fmt, command, key)
        # else:
        #     print "ohohohohohohoh"
        # else:
        #     raise

        # if (self.REPLICATE_DEBUG and (command != Command.ALIVE and command != Command.PUSH and command != Command.DISTRIBUTE and command !=Command.HEARTBEAT))\
        #         or self.ALIVE_PUSH_DEBUG and (command != Command.REPLICATE_PUT and command != Command.REPLICATE_REMOVE)\
        #         or (command != Command.ALIVE and command != Command.PUSH and command != Command.REPLICATE_PUT and command != Command.REPLICATE_REMOVE and command != Command.DISTRIBUTE and command !=Command.HEARTBEAT):
        Print.print_(str(self.successor[0]) + "," + str(self.successor[1])
                     + "send_request$ command:" + Command.print_command(command) \
                     + ", key: " + key \
                     + ", value_length: " \
                     + str(value_length) \
                     + ", value: " + str(value) \
                     + ", node id: " + str(node_overwrite) \
                     + ", stamp: " + vector_stamp_value
                     , Print.Wire, self.hashedKeyModN, cur_thread, command)

        #  Get the IP Port from the key
        if node_overwrite == -1:
            ip_port = NodeList.look_up_node_id(hash(key) % self.numberOfNodes, self.mode)
        else:  # Get it by node id
            ip_port = NodeList.look_up_node_id(node_overwrite, self.mode)

        local_ip_port = NodeList.look_up_node_id(self.hashedKeyModN, self.mode)
        # print ip_port
        if self.id == "epidemic":
            port = int(ip_port.split(':')[1]) + 1000
            # print "epidemic"
        elif self.id == "replicate":
            port = int(ip_port.split(':')[1]) + 500
        else:  # main
            port = ip_port.split(':')[1]
        self.RequestReplyClient_obj = RequestReplyClient.RequestReplyClient(ip_port.split(':')[0],
                                                                            port,
                                                                            msg,
                                                                            local_ip_port.split(':')[1],
                                                                            timeout,
                                                                            retrials,
                                                                            self.id)

        self.RequestReplyClient_obj.send()

    def receive_request(self, hashedKeyMod, cur_thread, handler=""):
        header, msg, addr, sixteen_byte_header = self.RequestReplyServer_obj.receive(cur_thread,
                                                                                     hashedKeyMod)
        # value2 = (None,)
        # value_length2 = (None,)
        vector_stamp_value = ''

        try:
            command, key = struct.unpack(self.fmtRequest, msg[0:33])
            if command == Command.JOIN_SUCCESSOR:
                print ''
            value_length = 0
            if command == Command.PUT or command == Command.JOIN_SUCCESSOR or command == Command.JOIN_PREDECESSOR or command == Command.ALIVE or command == Command.PUSH or command == Command.REPLICATE_PUT or command == Command.EXECUTE or command == Command.REPLICATE_EXECUTE or command == Command.EXECUTE_HINTED or command == Command.REPLICATE_GET or command == Command.DISTRIBUTE or command == Command.START_TEST:
                value_length = struct.unpack("H", msg[33:35])
                value_length = int(value_length[0])
                value_fmt = str(value_length) + 's'
                value = struct.unpack(value_fmt, msg[35:35 + value_length])

                # advance the local time
                # if command == Command.PUT or command == Command.REPLICATE_PUT or command == Command.REPLICATE_GET or command == Command.REPLICATE_REMOVE or command == Command.GET or command == Command.REMOVE:
            elif command == Command.COMMIT:
                value_length = struct.unpack("H", msg[33:35])
                value_length = int(value_length[0])
                value_fmt = str(value_length) + 's'
                value = struct.unpack(value_fmt, msg[37:37 + value_length])

                vector_stamp_value_length = struct.unpack("H", msg[35:37])
                vector_stamp_value_length = int(vector_stamp_value_length[0])
                value_fmt = str(vector_stamp_value_length) + 's'
                # try:
                vector_stamp_value = struct.unpack(value_fmt, msg[37 + value_length:37 + value_length + vector_stamp_value_length])
                vector_stamp_value = vector_stamp_value[0]
                # except:
                #     print "value_fmt:" + str(value_fmt) + ", value_length:" + str(value_length)+  "  , vector_stamp_value_length:" + str(vector_stamp_value_length)
                #     print "msg:" + msg
                #     print ", Command Received:" + Command.print_command(command)+ ", Key:" + key+ ", Value: "+ value[0]+ ", Value Length: " + str(value_length)
                #     raise
                VectorStamp.incoming_vector_stamp(vector_stamp_value)
                VectorStamp.advance_local_time_stamp()

            # elif command == Command.DISTRIBUTE:
            #     value_length = struct.unpack("H", msg[33:35])
            #     value_length = int(value_length[0])
            #     value_fmt = str(value_length) + 's'
            #     value = struct.unpack(value_fmt, msg[35:35 + value_length])
            # value_length2 = struct.unpack("H", msg[35 + value_length: 35 + value_length + 2])
            # value_length2 = int(value_length2[0])
            # value_fmt2 = str(value_length2) + 's'
            # value2 = struct.unpack(value_fmt2, msg[35 + value_length + 2: 35 + value_length + 2 + value_length2])

            else:  # Other commands like GET
                value = ("",)

            # if (self.REPLICATE_DEBUG and (command != Command.ALIVE and command != Command.PUSH and command != Command.DISTRIBUTE and command !=Command.HEARTBEAT))\
            #     or self.ALIVE_PUSH_DEBUG and (command != Command.REPLICATE_PUT and command != Command.REPLICATE_REMOVE)\
            #     or (command != Command.ALIVE and command != Command.PUSH and command != Command.REPLICATE_PUT and command != Command.REPLICATE_REMOVE and command != Command.DISTRIBUTE and command !=Command.HEARTBEAT):
            Print.print_(str(self.successor[0]) + "," + str(self.successor[1])
                         + "receive_request$ "
                         + str(addr)
                         + ", Command Received:"
                         + Command.print_command(command)
                         + ", Key:"
                         + key
                         + ", Value: "
                         + value[0]
                         + ", Value Length: "
                         + str(value_length)
                         + ", stamp: " + vector_stamp_value
                         , Print.Wire, self.hashedKeyModN, cur_thread, command)


        except:
            raise

        key = key.rstrip('\0')
        value = value[0]
        # value2 = value2[0]

        return command, key, value_length, value, addr, sixteen_byte_header

    def send_reply(self, sender_addr, key, response_code, value_length, value, cur_thread, command, sixteen_byte_header,
                   version="", origin_receiver=True):
        # version = ""
        version_length = 0
        # if command== Command.GET or command == Command.PUT or command == Command.REMOVE:
        #     version = Settings.kvTable[key].version
        #     version_length = len(version)
        Print.print_(str(self.successor[0]) + "," + str(self.successor[1]) +
                     "send_reply$ " + str(sender_addr) +
                     ", response_code: " + Response.print_response(response_code) +
                     ", value: " + value +
                     ", value length: " + str(value_length) +
                     ", mode: " + Mode.print_mode(self.mode) +
                     ", command: " + Command.print_command(command)
                     , Print.Wire, self.hashedKeyModN, cur_thread, command)

        fmt = self.fmtReply
        # Modify such that don't send the value length and the value except for teh GET PING and ALIVE
        if value_length != 0:
            fmt += 'H' + str(value_length) + 's'
            fmt += 'H' + str(version_length) + 's'
            msg = struct.pack(fmt, response_code, value_length, value, version_length, version)
            # msg = struct.pack(fmt, response_code, value_length, value)

            # print "response_code", response_code
            # print "msg", msg
        else:
            msg = struct.pack(fmt, response_code)
        self.RequestReplyServer_obj.send_reply(sender_addr[0], sender_addr[1], msg, command, key, self.hashedKeyModN,
                                               sixteen_byte_header, origin_receiver)

    def receive_reply(self, cur_thread, command):
        request_reply_response = self.RequestReplyClient_obj.receive_reply(command, self.hashedKeyModN, cur_thread)
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
            # except:
            #     raise

            Print.print_(str(self.successor[0]) + "," + str(self.successor[1]) +
                         "receive_reply$ response:" + Response.print_response(response_code) +
                         ", value:" + str(value[0]) +
                         ", mode: " + Mode.print_mode(self.mode) +
                         ", command: " + Command.print_command(command)
                         # ", version: " + version
                         , Print.Wire, self.hashedKeyModN, cur_thread, command)

            # return response_code, value[0]
        return response_code, value[0], version
