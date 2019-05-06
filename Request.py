class Request:
    def __init__(self, client_id, start, end):
        self.status = 'Processing'
        self.taxi = None
        self.client_id = client_id
        self.start = start
        self.end = end