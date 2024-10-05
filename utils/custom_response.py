class CustomResponse:
    def __init__(self, status_code: int, message: str, result=None):
        self.status_code = status_code
        self.message = message
        self.result = result
