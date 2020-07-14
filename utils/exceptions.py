class CustomBaseException(Exception):
    def __init__(self):
        self.status_code = 400


class NotFound(CustomBaseException):
    def __init__(self, message='The requested resource was not found'):
        super().__init__()
        self.message = message
        self.status_code = 404


class AccessDenied(CustomBaseException):
    def __init__(self, message='Access Denied'):
        super().__init__()
        self.message = message
        self.status_code = 401
