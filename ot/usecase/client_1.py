from ot.test_text_operation import random_string, random_operation
from ot.client import Client
from threading import Thread
from interpreter import LoteosMain
from thin_server.LoteosThinServerSupport import incoming_requests_q

loteos_main_obj = LoteosMain.Loteos()
loteos_main_obj.start_thin_client_and_server()


class MyClient(Client):
    def __init__(self, revision, id, document):
        Client.__init__(self, revision)
        self.id = id
        self.document = document

    def send_operation(self, revision, operation):
        # server_q.put((self.id, revision, operation))
        msg = (self.id, revision, operation)

        loteos_main_obj.run(
            """
            publish(@msg);            
            """, locals(), globals()
        )
        print "client 1 sent: " + str(msg)

    def apply_operation(self, operation):
        self.document = operation(self.document)

    def perform_operation(self):
        operation = random_operation(self.document)
        self.document = operation(self.document)
        self.apply_client(operation)


# Todo: get this queues and map them to loteos
# Todo: or use loteos directly
# or use thin interpreters object

# server_q = Queue()
# client_1_q = Queue()


def client_1(document):
    # document
    client1 = MyClient(0, 'client1', document)

    loteos_main_obj.run(
        """
        register(0);    
        """
        )

    loteos_main_obj.run(
        """
        subscribe(2);
        """
    )

    def client_1_receive():
        while True:
            # msg = client_1_q.get()
            msg = incoming_requests_q.get()
            print "client 1 received: " + str(msg)
            (client_id, operation) = msg
            if client1.id == client_id:
                client1.server_ack()
            else:
                client1.apply_server(operation)
            # print "client 1 document after received msg: " + str(document)

    # receive
    thread = Thread(target=client_1_receive)
    thread.start()

    # print the doc state before
    # print "client 1 before:" + client1.document

    # execute random operation
    client1.perform_operation()
    # print the doc state after

    print "client document after: " + client1.document
    # check the change


if __name__ == '__main__':
    # Initialize document to distributed object in the key-store store
    document = random_string()
    loteos_main_obj.run(
        """
        var x = read("document");
        if (x == "") write("document", @document); else @document = x;
        """, locals(), globals()
    )
    print "client initial document state: " + document
    thread_1 = Thread(target=client_1, args=(document,))
    thread_1.start()


