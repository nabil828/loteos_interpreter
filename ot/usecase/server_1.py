from ot.test_text_operation import random_string, random_operation

from ot.client import Client
from ot.server import MemoryBackend, Server
from threading import Thread
from Queue import Queue
from interpreter import LoteosMain
from thin_server.LoteosThinServerSupport import incoming_requests_q

loteos_main_obj = LoteosMain.Loteos()
loteos_main_obj.start_thin_client_and_server()


def server(document_):
    server_ = Server(document_, MemoryBackend())
    loteos_main_obj.run(
        """
        register(2);    
        """
        )

    loteos_main_obj.run(
        """
        subscribe(0);
        subscribe(1);
        """
    )

    def server_receive():
        while True:
            msg = incoming_requests_q.get()
            (client_id, revision, operation) = msg
            print "server 1 received:" + str(msg)
            operation_p = server_.receive_operation(client_id, revision, operation)

            msg = (client_id, operation_p)
            # # client1_receive_channel.write(msg)
            # client_1_q.put(msg)
            # # client2_receive_channel.write(msg)
            # client_2_q.put(msg)
            loteos_main_obj.run(
                """
                publish(@msg);            
                """, locals()
            )
            print "server 1 sent:" + str(msg)
            print "server's document after receiving:" + server_.document

    # receive
    thread = Thread(target=server_receive)
    thread.start()

    # # Check the queue
    # while True:
    #     # msg = server_q.get()
    #     msg = incoming_requests_q.get()
    #     server_receive(msg)


if __name__ == '__main__':
    # Run client 1
    # Run client 2
    # Run server
    document = random_string()
    loteos_main_obj.run(
        """
        var x = read("document");
        if (x == "") write("document", @document); else @document = x;
        """, locals(), globals()
    )
    print "Server initial document state:" + document

    thread_3 = Thread(target=server, args=(document,))
    thread_3.start()
