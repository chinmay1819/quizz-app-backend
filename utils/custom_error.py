
class CustomError(Exception):
    def __init__(self, status_code: int = 500, message: str = "", error: any = None):
        super().__init__(message)
        self.status_code = status_code
        # self.timestamp = datetime.now().isoformat()
        self.error = error
