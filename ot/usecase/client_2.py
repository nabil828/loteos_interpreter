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
            """, locals()
        )
        # pass

    def apply_operation(self, operation):
        self.document = operation(self.document)

    def perform_operation(self):
        operation = random_operation(self.document)
        self.document = operation(self.document)
        self.apply_client(operation)


def client_2(document):
    # document
    client2 = MyClient(0, 'client2', document)

    loteos_main_obj.run(
        """
        register(1);    
        """
    )

    loteos_main_obj.run(
        """
        subscribe(2);
        """
    )

    def client_2_receive():
        while True:
            msg = incoming_requests_q.get()
            print "client 2 received: " + str(msg)
            (client_id, operation) = msg
            if client2.id == client_id:
                client2.server_ack()
            else:
                client2.apply_server(operation)

            print "client document after receiving: " + client2.document
            # check the change

    # receive
    thread = Thread(target=client_2_receive)
    thread.start()


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
    thread_2 = Thread(target=client_2, args=(document,))
    thread_2.start()





