import Queue

outgoing_requests_q = Queue.Queue()
response_q = Queue.Queue()


class ResponseObj:
    def __init__(self, response, value, version):
        self.response = response
        self.value = value # to be send back to COMMIT
        # self.node_id = node_id
        self.version = version


class QueueObj:
    def __init__(self, command, key, value):
        self.command = command
        self.key = key
        self.value = value
