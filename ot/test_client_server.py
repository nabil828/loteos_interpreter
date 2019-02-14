from test_text_operation import random_string, random_operation

from ot.client import Client
from ot.server import MemoryBackend, Server
from threading import Thread
from Queue import Queue


class MyClient(Client):
    def __init__(self, revision, id, document):
        Client.__init__(self, revision)
        self.id = id
        self.document = document

    def send_operation(self, revision, operation):
        server_q.put((self.id, revision, operation))
        pass

    def apply_operation(self, operation):
        self.document = operation(self.document)

    def perform_operation(self):
        operation = random_operation(self.document)
        self.document = operation(self.document)
        self.apply_client(operation)

server_q = Queue()
client_1_q = Queue()
client_2_q = Queue()


def server(document):
    server = Server(document, MemoryBackend())

    def server_receive(msg):
        (client_id, revision, operation) = msg
        operation_p = server.receive_operation(client_id, revision, operation)

        msg = (client_id, operation_p)
        # client1_receive_channel.write(msg)
        client_1_q.put(msg)
        # client2_receive_channel.write(msg)
        client_2_q.put(msg)
        print "server:" + server.document

    # Check the queue
    while True:
        msg = server_q.get()
        server_receive(msg)


if __name__ == '__main__':
    # Run client 1
    # Run client 2
    # Run server
    document = random_string()
    print "document:" + document
    thread_3 = Thread(target=server, args=(document,))
    thread_3.start()
